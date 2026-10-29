-- STEP 3: 주문 생성과 결제는 서버 전용 RPC에서 트랜잭션으로 처리한다.
CREATE OR REPLACE FUNCTION public.create_order(p_user_id uuid, p_order_id uuid)
RETURNS uuid LANGUAGE plpgsql SECURITY INVOKER SET search_path = public AS $$
DECLARE item record;
BEGIN
    PERFORM 1 FROM orders WHERE id = p_order_id AND user_id = p_user_id AND status = 'cart' FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'CART_NOT_FOUND'; END IF;
    IF NOT EXISTS (SELECT 1 FROM order_items WHERE order_id = p_order_id) THEN RAISE EXCEPTION 'CART_EMPTY'; END IF;
    FOR item IN SELECT oi.id, oi.quantity, p.price, p.stock FROM order_items oi JOIN products p ON p.id = oi.product_id WHERE oi.order_id = p_order_id ORDER BY p.id FOR UPDATE OF p LOOP
        IF item.stock < item.quantity THEN RAISE EXCEPTION 'INSUFFICIENT_STOCK'; END IF;
        UPDATE order_items SET unit_price = item.price WHERE id = item.id;
    END LOOP;
    UPDATE orders SET status = 'pending', updated_at = now() WHERE id = p_order_id;
    RETURN p_order_id;
END;
$$;

CREATE OR REPLACE FUNCTION public.pay_order(p_user_id uuid, p_order_id uuid, p_success boolean)
RETURNS uuid LANGUAGE plpgsql SECURITY INVOKER SET search_path = public AS $$
DECLARE item record; total bigint; payment_id uuid;
BEGIN
    PERFORM 1 FROM orders WHERE id = p_order_id AND user_id = p_user_id AND status = 'pending' FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'ORDER_NOT_PENDING'; END IF;
    SELECT sum(quantity::bigint * unit_price) INTO total FROM order_items WHERE order_id = p_order_id;
    IF total IS NULL THEN RAISE EXCEPTION 'CART_EMPTY'; END IF;
    IF p_success THEN
        -- 항상 상품 ID 순서로 잠가 동시 결제 시 재고가 중복 차감되지 않게 한다.
        FOR item IN SELECT oi.quantity, p.id, p.stock FROM order_items oi JOIN products p ON p.id = oi.product_id WHERE oi.order_id = p_order_id ORDER BY p.id FOR UPDATE OF p LOOP
            IF item.stock < item.quantity THEN RAISE EXCEPTION 'INSUFFICIENT_STOCK'; END IF;
            UPDATE products SET stock = stock - item.quantity, updated_at = now() WHERE id = item.id;
        END LOOP;
    END IF;
    INSERT INTO payments (order_id, amount, status) VALUES (p_order_id, total, CASE WHEN p_success THEN 'success' ELSE 'failed' END)
    ON CONFLICT (order_id) DO UPDATE SET amount = EXCLUDED.amount, status = EXCLUDED.status, created_at = now()
    RETURNING id INTO payment_id;
    IF p_success THEN UPDATE orders SET status = 'paid', updated_at = now() WHERE id = p_order_id; END IF;
    RETURN payment_id;
END;
$$;

-- 공개 키와 일반 사용자에게 RPC 호출 권한을 주지 않는다.
REVOKE ALL ON FUNCTION public.create_order(uuid, uuid) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.pay_order(uuid, uuid, boolean) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.create_order(uuid, uuid) TO service_role;
GRANT EXECUTE ON FUNCTION public.pay_order(uuid, uuid, boolean) TO service_role;

CREATE OR REPLACE FUNCTION public.cart_add_item(p_user_id uuid, p_product_id uuid, p_quantity integer)
RETURNS uuid LANGUAGE plpgsql SECURITY INVOKER SET search_path = public AS $$
DECLARE cart_id uuid; item_id uuid; current_quantity integer; product_price integer; product_stock integer;
BEGIN
    IF p_quantity < 1 OR p_quantity > 10000 THEN RAISE EXCEPTION 'INVALID_QUANTITY'; END IF;
    INSERT INTO orders (user_id, status) VALUES (p_user_id, 'cart')
    ON CONFLICT (user_id) WHERE status = 'cart' DO NOTHING;
    SELECT id INTO cart_id FROM orders WHERE user_id = p_user_id AND status = 'cart' FOR UPDATE;
    SELECT price, stock INTO product_price, product_stock FROM products WHERE id = p_product_id;
    IF NOT FOUND THEN RAISE EXCEPTION 'PRODUCT_NOT_FOUND'; END IF;
    SELECT quantity INTO current_quantity FROM order_items WHERE order_id = cart_id AND product_id = p_product_id;
    IF COALESCE(current_quantity, 0) + p_quantity > 10000 THEN RAISE EXCEPTION 'INVALID_QUANTITY'; END IF;
    IF COALESCE(current_quantity, 0) + p_quantity > product_stock THEN RAISE EXCEPTION 'INSUFFICIENT_STOCK'; END IF;
    INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (cart_id, p_product_id, p_quantity, product_price)
    ON CONFLICT (order_id, product_id) DO UPDATE SET quantity = order_items.quantity + EXCLUDED.quantity, unit_price = EXCLUDED.unit_price
    RETURNING id INTO item_id;
    RETURN item_id;
END;
$$;

CREATE OR REPLACE FUNCTION public.cart_update_item(p_user_id uuid, p_item_id uuid, p_quantity integer)
RETURNS void LANGUAGE plpgsql SECURITY INVOKER SET search_path = public AS $$
DECLARE cart_id uuid; available integer;
BEGIN
    IF p_quantity < 1 OR p_quantity > 10000 THEN RAISE EXCEPTION 'INVALID_QUANTITY'; END IF;
    SELECT id INTO cart_id FROM orders WHERE user_id = p_user_id AND status = 'cart' FOR UPDATE;
    SELECT p.stock INTO available FROM order_items oi JOIN products p ON p.id = oi.product_id WHERE oi.id = p_item_id AND oi.order_id = cart_id;
    IF NOT FOUND THEN RAISE EXCEPTION 'ITEM_NOT_FOUND'; END IF;
    IF p_quantity > available THEN RAISE EXCEPTION 'INSUFFICIENT_STOCK'; END IF;
    UPDATE order_items SET quantity = p_quantity WHERE id = p_item_id AND order_id = cart_id;
END;
$$;

CREATE OR REPLACE FUNCTION public.cart_delete_item(p_user_id uuid, p_item_id uuid)
RETURNS void LANGUAGE plpgsql SECURITY INVOKER SET search_path = public AS $$
DECLARE cart_id uuid;
BEGIN
    SELECT id INTO cart_id FROM orders WHERE user_id = p_user_id AND status = 'cart' FOR UPDATE;
    DELETE FROM order_items WHERE id = p_item_id AND order_id = cart_id;
    IF NOT FOUND THEN RAISE EXCEPTION 'ITEM_NOT_FOUND'; END IF;
END;
$$;

REVOKE ALL ON FUNCTION public.cart_add_item(uuid, uuid, integer) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.cart_update_item(uuid, uuid, integer) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.cart_delete_item(uuid, uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.cart_add_item(uuid, uuid, integer) TO service_role;
GRANT EXECUTE ON FUNCTION public.cart_update_item(uuid, uuid, integer) TO service_role;
GRANT EXECUTE ON FUNCTION public.cart_delete_item(uuid, uuid) TO service_role;
