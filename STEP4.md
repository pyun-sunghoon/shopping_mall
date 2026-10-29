# STEP 4 실행 및 확인

STEP 1~3 설정이 완료된 프로젝트에서 PowerShell로 서버를 실행합니다.

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/docs`에서 확인합니다. 회원 탈퇴는 되돌리기 어려우므로 별도 테스트 계정을 사용하세요.

1. 로그인하지 않고 `GET /api/me`를 호출하면 401입니다.
2. 테스트 계정으로 `POST /api/auth/login`을 호출합니다.
3. `GET /api/me`로 본인의 정보를 조회합니다.
4. `PATCH /api/me`에 다음 예시를 입력하고, 다시 조회해 변경을 확인합니다.

```json
{"name":"테스트 사용자","phone":"010-1111-2222","address":"서울시 테스트 주소"}
```

5. `GET /api/me/orders`에서 본인의 결제 완료 주문을 확인합니다. 결제한 주문이 없으면 빈 배열입니다.
6. `POST /api/me/password`에서 현재 비밀번호와 새 비밀번호를 입력합니다. 변경 후 다시 로그인합니다. 잘못된 현재 비밀번호는 401입니다.

```json
{"current_password":"기존 비밀번호","new_password":"새 비밀번호 8자 이상"}
```

7. 별도 테스트 계정으로 `DELETE /api/me`에 현재 비밀번호를 입력합니다. 이후 같은 계정으로 로그인하면 401이고, DB의 회원 행과 기존 구매내역은 남습니다.

```json
{"password":"현재 비밀번호"}
```

비밀번호 변경은 현재 브라우저의 쿠키를 삭제합니다. 이전에 발급된 다른 JWT는 만료 전까지 유효합니다. 탈퇴한 회원의 JWT는 회원 상태 확인으로 거부됩니다.
