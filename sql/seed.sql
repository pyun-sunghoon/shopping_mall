-- 샘플 상품: 가격은 원 단위, 재고는 개수다. 한 번만 실행한다.
INSERT INTO public.products (name, description, price, stock, image_url) VALUES
    ('베이직 티셔츠', '편하게 입는 기본 반팔 티셔츠', 19000, 30, NULL),
    ('캔버스 에코백', '가볍게 들 수 있는 캔버스 가방', 15000, 20, NULL),
    ('스테인리스 텀블러', '일상에서 사용하는 500ml 텀블러', 25000, 15, NULL);
