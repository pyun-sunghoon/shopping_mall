# STEP 2 실행 및 확인

## 준비

1. STEP 1의 `schema.sql`을 Supabase SQL Editor에서 실행합니다.
2. Supabase 프로젝트의 URL과 서버 전용 `service_role` 키를 확인합니다. 키를 브라우저나 공개 저장소에 넣지 마세요.
3. 프로젝트 폴더의 PowerShell에서 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

4. `.env`에 Supabase URL, service role 키, 32자 이상의 무작위 `SECRET_KEY`를 입력합니다. 로컬 HTTP에서는 `COOKIE_SECURE=false`를 유지합니다. HTTPS 배포 시에는 `true`로 설정합니다.
5. 서버를 시작합니다.

```powershell
uvicorn app.main:app --reload
```

## Swagger 확인

브라우저에서 `http://127.0.0.1:8000/docs`를 엽니다.

1. `POST /api/auth/register`에서 다음 JSON으로 가입합니다.

```json
{"email":"test@example.com","password":"password123","name":"홍길동","phone":"010-1234-5678","address":"서울시"}
```

2. `POST /api/auth/login`에 같은 이메일과 비밀번호를 입력합니다. 성공 시 HttpOnly 쿠키가 설정됩니다.
3. `POST /api/auth/logout`을 호출해 쿠키를 삭제합니다.
4. 같은 이메일로 재가입하면 409, 잘못된 비밀번호로 로그인하면 401을 확인합니다.

로그아웃은 현재 브라우저의 쿠키를 삭제합니다. 이미 복사된 JWT는 만료 전까지 유효하며, 보호 API는 후속 단계에서 연결합니다.
