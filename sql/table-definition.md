# 테이블 정의서

실제 생성 제약조건은 [schema.sql](schema.sql)을 기준으로 합니다. 금액은 원 단위이며, 시간은 시간대를 포함합니다. PK는 기본 키, FK는 외래 키입니다. `NOT NULL`은 필수 값입니다.

## users — 회원

| 컬럼 | 자료형 | 필수 | 키·제약·기본값 |
|---|---|---|---|
| id | uuid | 예 | PK, 자동 생성 |
| email | text | 예 | UNIQUE |
| password_hash | text | 예 | 비밀번호 해시 |
| name | text | 예 | |
| phone | text | 예 | |
| address | text | 예 | |
| created_at | timestamptz | 예 | 기본값 현재 시각 |
| updated_at | timestamptz | 예 | 기본값 현재 시각 |
| deleted_at | timestamptz | 아니요 | 탈퇴 시각, 기본값 NULL |

## products — 상품

| 컬럼 | 자료형 | 필수 | 키·제약·기본값 |
|---|---|---|---|
| id | uuid | 예 | PK, 자동 생성 |
| name | text | 예 | |
| description | text | 예 | 기본값 빈 문자열 |
| price | integer | 예 | 0 이상 |
| stock | integer | 예 | 0 이상, 기본값 0 |
| image_url | text | 아니요 | 기본값 NULL |
| created_at | timestamptz | 예 | 기본값 현재 시각 |
| updated_at | timestamptz | 예 | 기본값 현재 시각 |

## orders — 장바구니와 주문

| 컬럼 | 자료형 | 필수 | 키·제약·기본값 |
|---|---|---|---|
| id | uuid | 예 | PK, 자동 생성 |
| user_id | uuid | 예 | FK → users.id, 삭제 제한 |
| status | text | 예 | `cart`, `pending`, `paid` 중 하나, 기본값 `cart` |
| created_at | timestamptz | 예 | 기본값 현재 시각 |
| updated_at | timestamptz | 예 | 기본값 현재 시각 |

회원별 `cart` 상태는 부분 UNIQUE 인덱스로 하나만 허용합니다.

## order_items — 장바구니·주문 상품

| 컬럼 | 자료형 | 필수 | 키·제약·기본값 |
|---|---|---|---|
| id | uuid | 예 | PK, 자동 생성 |
| order_id | uuid | 예 | FK → orders.id, 주문 삭제 시 함께 삭제 |
| product_id | uuid | 예 | FK → products.id, 삭제 제한 |
| quantity | integer | 예 | 1 이상 |
| unit_price | integer | 예 | 0 이상, 주문 시점 단가 |

`(order_id, product_id)` 조합은 UNIQUE입니다.

## payments — 결제 결과

| 컬럼 | 자료형 | 필수 | 키·제약·기본값 |
|---|---|---|---|
| id | uuid | 예 | PK, 자동 생성 |
| order_id | uuid | 예 | FK → orders.id, UNIQUE, 삭제 제한 |
| amount | bigint | 예 | 0 이상 |
| status | text | 예 | `success` 또는 `failed` |
| created_at | timestamptz | 예 | 기본값 현재 시각 |

모든 테이블에 RLS가 활성화되어 있으며 공개 접근 정책은 없습니다. `updated_at`은 수정 시 애플리케이션에서 갱신합니다. 탈퇴 회원의 이메일 UNIQUE는 유지됩니다.
