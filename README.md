# 쇼핑몰 MVP

FastAPI가 HTML·CSS·Vanilla JavaScript와 API를 함께 제공합니다. DB는 Supabase PostgreSQL이며, 회원 비밀번호는 bcrypt 해시로 저장합니다. 인증은 HttpOnly 쿠키의 JWT를 사용합니다. 실제 결제 대행사는 연결하지 않습니다.

## 로컬 실행

VS Code에서 이 프로젝트 폴더를 열고 PowerShell 터미널에서 실행합니다. Python과 pip가 설치되어 있어야 합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

이미 `.env`가 있다면 복사 명령을 생략하여 기존 설정을 유지합니다. 활성화가 제한되면 다음처럼 가상환경 Python을 직접 사용합니다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

`.env`를 다음 표에 맞춰 입력하고 DB 설정을 완료합니다.

| 변수 | 로컬 값 | 설명 |
|---|---|---|
| SUPABASE_URL | 프로젝트 URL | `https://프로젝트ID.supabase.co` 형태 |
| SUPABASE_SERVICE_ROLE_KEY | 서버 전용 service_role 키 | 브라우저에 노출하지 않음 |
| SECRET_KEY | 32자 이상의 무작위 비밀값 | 이 앱의 JWT 서명용, Supabase 키와 별개 |
| COOKIE_SECURE | false | 로컬 HTTP용 |

비밀값 생성 예시입니다. 출력값을 `.env`의 `SECRET_KEY`에 입력합니다.

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

서버는 프로젝트 루트에서 시작합니다.

```powershell
uvicorn app.main:app --reload
```

- 화면: [로컬 상점](http://127.0.0.1:8000/)
- API 호출: [Swagger](http://127.0.0.1:8000/docs)

## Supabase 설정

1. Supabase에서 프로젝트를 선택합니다.
2. 프로젝트의 Connect에서 Project URL을 확인합니다.
3. Settings → API Keys에서 서버 전용 키를 확인합니다. 현재 설정명은 기존 `service_role` 기준입니다. `anon` 또는 publishable 키는 서버 관리자 키로 사용하지 않습니다.
4. SQL Editor에서 다음 파일을 순서대로 붙여넣고 실행합니다.

| 순서 | 파일 | 내용 |
|---|---|---|
| 1 | [schema.sql](sql/schema.sql) | 테이블, 관계, RLS |
| 2 | [seed.sql](sql/seed.sql) | 샘플 상품 3개 |
| 3 | [step3.sql](sql/step3.sql) | 장바구니·주문·결제 함수 |
| 4 | [step5.sql](sql/step5.sql) | 바로 결제 주문 함수 |

이미 설정한 DB에서는 `schema.sql`과 `seed.sql`을 재실행하지 않습니다. 특히 seed 재실행은 상품을 중복 생성합니다. 함수 파일은 갱신 시 다시 실행할 수 있습니다. 이 앱은 Supabase Auth 대신 자체 users 테이블을 사용하므로 회원가입은 상점 화면에서 진행합니다.

테이블 직접 접근은 RLS로 차단하고 서버가 service role 권한으로 DB를 호출합니다. 서버 API는 현재 로그인한 회원의 ID로 데이터 접근 범위를 제한합니다.

## Render 배포

저장소 루트에 `render.yaml`, `requirements.txt`, `app`, `static`, `templates`가 함께 있도록 GitHub 또는 GitLab 저장소에 소스를 올립니다. `.env`와 `.venv`는 올리지 않습니다. 이 프로젝트의 `.gitignore`에 제외되어 있습니다.

1. Render에 로그인하고 New → Blueprint에서 저장소를 연결합니다.
2. 배포할 브랜치를 선택하고 루트의 `render.yaml`을 사용합니다. 프로젝트가 저장소의 하위 폴더라면 설정 파일과 작업 루트를 그 폴더에 맞춰 지정해야 합니다.
3. 요청되는 `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` 값을 입력합니다.
4. 생성될 Web Service 설정과 플랜을 확인한 후 사용자가 배포를 시작합니다.
5. 배포 로그에서 설치와 Uvicorn 시작 결과를 확인하고 제공된 HTTPS 주소를 엽니다.

Blueprint는 다음 환경변수를 설정합니다.

| 변수 | Render 설정 |
|---|---|
| SUPABASE_URL | 사용자가 입력 |
| SUPABASE_SERVICE_ROLE_KEY | 사용자가 입력 |
| SECRET_KEY | Render에서 무작위 생성 |
| COOKIE_SECURE | true |

기존 서비스의 변수 수정은 해당 서비스의 Environment에서 수행합니다. 저장 후 재배포하여 적용합니다. 로컬 `.env` 파일을 Render에 올릴 필요는 없습니다.

수동으로 Web Service를 생성한다면 Runtime은 Python, Build Command와 Start Command는 아래와 같습니다.

```text
pip install -r requirements.txt
```

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

`$PORT`는 Render가 제공하는 값입니다. 배포에서는 `--reload`를 사용하지 않습니다. 이 설정은 무료 플랜을 가정하며 계정에서 사용 가능한 플랜과 조건은 생성 화면에서 확인합니다.

Render 설정 방식: [FastAPI 배포 안내](https://render.com/docs/deploy-fastapi), [Blueprint 설정과 환경변수](https://render.com/docs/blueprint-spec).

## 배포 후 사용자 확인

| 항목 | 확인 방법 |
|---|---|
| 상품 조회 | 배포 주소에서 샘플 상품과 상세 확인 |
| 회원가입·로그인 | 테스트 계정 가입 후 로그인 |
| 인증 복귀 | 로그아웃 → 장바구니 → 로그인 → 장바구니 복귀 |
| 주문·결제 | 상품 담기 → 주문 → 모의 결제 → 구매내역 확인 |
| 바로 결제 | 상품 상세 → 바로 결제 → 결제 완료 |
| 회원정보 | 이름·연락처·주소 수정 후 재조회 |
| 모바일 화면 | F12에서 360px, 768px, 1200px 확인 |

모의 결제 성공 시 DB 재고가 차감됩니다. 탈퇴 검증은 별도 테스트 계정으로 수행합니다.

## 오류 확인

- 상품 조회가 실패하면 Render 로그와 Supabase URL·서버 키를 확인합니다.
- 바로 결제만 500이면 `step5.sql` 적용 여부와 서버 traceback을 확인합니다.
- 로그인 후 인증이 유지되지 않으면 HTTPS 주소 사용과 `COOKIE_SECURE=true`를 확인합니다.
- 로컬 HTTP에서는 `COOKIE_SECURE=false`로 설정합니다. 변경 후 서버를 재시작합니다.
- JWT 비밀키를 바꾸면 기존 로그인 토큰이 무효화되어 다시 로그인해야 합니다.

## 문서와 현재 검증 범위

[ERD](sql/ERD.md) · [테이블 정의](sql/table-definition.md) · [구매 시뮬레이션](sql/purchase-simulation.md)

[STEP 2](STEP2.md) · [STEP 3](STEP3.md) · [STEP 4](STEP4.md) · [STEP 5](STEP5.md) · [STEP 6](STEP6.md) · [STEP 6 테스트 결과](STEP6-test-results.md)

로컬에서 주요 API와 장바구니·바로 결제 및 일부 인증 복귀 흐름을 확인했습니다. 360px·768px·1200px 화면 검증, 재고 부족 시나리오, 구매한 회원 탈퇴 후 내역 보존 및 배포 환경 동작은 확인이 남아 있습니다. 배포는 수행하지 않았습니다.

로그아웃과 비밀번호 변경은 현재 브라우저의 쿠키를 삭제합니다. 이미 복사된 JWT는 만료 전까지 유효하며, 탈퇴 회원은 서버의 회원 상태 확인으로 차단됩니다.
