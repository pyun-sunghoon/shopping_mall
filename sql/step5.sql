-- 바로 결제는 기존 장바구니를 건드리지 않고 결제 대기 주문을 생성한다.
CREATE OR REPLACE FUNCTION public.create_direct_order(p_user_id uuid, p_product_id uuid, p_quantity integer)
RETURNS uuid LANGUAGE plpgsql SECURITY INVOKER SET search_path = public AS $$
DECLARE product_price integer; product_stock integer; order_id uuid;
BEGIN
    IF p_quantity < 1 OR p_quantity > 10000 THEN RAISE EXCEPTION 'INVALID_QUANTITY'; END IF;
    SELECT price, stock INTO product_price, product_stock FROM products WHERE id = p_product_id FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'PRODUCT_NOT_FOUND'; END IF;
    IF product_stock < p_quantity THEN RAISE EXCEPTION 'INSUFFICIENT_STOCK'; END IF;
    INSERT INTO orders (user_id, status) VALUES (p_user_id, 'pending') RETURNING id INTO order_id;
    INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (order_id, p_product_id, p_quantity, product_price);
    RETURN order_id;
END;
$$;
REVOKE ALL ON FUNCTION public.create_direct_order(uuid, uuid, integer) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.create_direct_order(uuid, uuid, integer) TO service_role;
