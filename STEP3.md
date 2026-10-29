# STEP 3 실행 및 확인

## 준비

STEP 1의 `schema.sql`과 `seed.sql`이 실행된 Supabase 프로젝트에서 [step3.sql](sql/step3.sql)을 SQL Editor에 붙여넣고 실행합니다. 기존 데이터를 삭제하지 않습니다.

프로젝트 폴더에서 서버를 실행합니다.

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/docs`에서 다음 순서로 호출합니다. 응답의 ID는 본인의 값으로 사용합니다.

| 순서 | API | 입력과 기대 결과 |
|---|---|---|
| 1 | `GET /api/products` | 로그인 없이 호출하고 상품의 `id`와 `stock` 확인 |
| 2 | `GET /api/products/{product_id}` | 상품 ID를 입력해 상세 정보 확인 |
| 3 | `GET /api/cart` | 로그인 전 401 확인 |
| 4 | `POST /api/auth/login` | STEP 2에서 가입한 계정으로 로그인 |
| 5 | `POST /api/cart/items` | `{"product_id":"상품 UUID","quantity":2}` 입력, `item_id` 확인 |
| 6 | `GET /api/cart` | 담긴 상품과 수량 확인 |
| 7 | `PATCH /api/cart/items/{item_id}` | `{"quantity":1}`로 변경 후 장바구니 조회 |
| 8 | `DELETE /api/cart/items/{item_id}` | 항목 삭제 후 장바구니 조회; 이후 다시 상품 담기 |
| 9 | `POST /api/orders` | 응답의 결제 대기 `order_id` 확인 |
| 10 | `POST /api/orders/{order_id}/payment` | `{"success":false}`로 실패 저장 후 `{"success":true}`로 재시도 |
| 11 | `GET /api/products/{product_id}` | 결제 성공 후 재고가 주문 수량만큼 감소했는지 확인 |

재고보다 많은 수량을 담거나 변경하면 409를 확인합니다. 주문 생성 후 다른 구매로 재고가 부족해진 경우 결제 시에도 409가 반환되며 재고 차감과 성공 처리는 취소됩니다. 이미 결제된 주문을 다시 결제하면 404입니다.

로그인 쿠키는 Swagger를 연 브라우저에서 사용합니다. API 변경 후 서버가 갱신되지 않았다면 서버를 재시작하세요.
