-- STEP 1: 쇼핑몰 MVP 스키마 (새 프로젝트에서 한 번 실행)
CREATE TABLE public.users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    name text NOT NULL,
    phone text NOT NULL,
    address text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    deleted_at timestamptz
);

CREATE TABLE public.products (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    price integer NOT NULL CHECK (price >= 0),
    stock integer NOT NULL DEFAULT 0 CHECK (stock >= 0),
    image_url text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- cart는 장바구니, pending은 결제 대기, paid는 결제 완료 상태다.
CREATE TABLE public.orders (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    status text NOT NULL DEFAULT 'cart' CHECK (status IN ('cart', 'pending', 'paid')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
-- 사용자별 활성 장바구니는 하나만 허용한다.
CREATE UNIQUE INDEX orders_one_cart_per_user ON public.orders (user_id) WHERE status = 'cart';
CREATE INDEX orders_user_created_idx ON public.orders (user_id, created_at DESC);

CREATE TABLE public.order_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    product_id uuid NOT NULL REFERENCES public.products(id) ON DELETE RESTRICT,
    quantity integer NOT NULL CHECK (quantity > 0),
    -- 주문 생성 시점의 단가를 저장해 이후 상품 가격 변경과 분리한다.
    unit_price integer NOT NULL CHECK (unit_price >= 0),
    UNIQUE (order_id, product_id)
);

CREATE TABLE public.payments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid NOT NULL UNIQUE REFERENCES public.orders(id) ON DELETE RESTRICT,
    amount bigint NOT NULL CHECK (amount >= 0),
    status text NOT NULL CHECK (status IN ('success', 'failed')),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- 클라이언트 공개 키로 직접 테이블에 접근하지 못하도록 기본 차단한다.
-- 서버는 향후 service role 키를 사용하며, 이 키는 브라우저에 노출하지 않는다.
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
