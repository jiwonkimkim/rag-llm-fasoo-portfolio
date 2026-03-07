# GitHub 저장소 연동 가이드

이 문서는 로컬 폴더를 GitHub 저장소에 연동하는 방법을 설명합니다.

---

## 1. 사전 준비

### 1.1 GitHub CLI 설치 확인
```bash
gh --version
```

### 1.2 GitHub 로그인 상태 확인
```bash
gh auth status
```

**출력 예시:**
```
github.com
  ✓ Logged in to github.com account neonardo-khan (keyring)
  - Active account: true
```

### 1.3 로그인이 안 되어 있다면
```bash
gh auth login
```
- 브라우저에서 인증 진행

### 1.4 계정 전환이 필요한 경우
```bash
# 다른 계정으로 전환
gh auth switch -u 계정이름
```

---

## 2. 새 폴더에서 시작하는 경우

### 2.1 폴더 생성 및 이동
```bash
mkdir "프로젝트명"
cd "프로젝트명"
```

### 2.2 Git 초기화
```bash
git init
```

### 2.3 Remote 저장소 연결
```bash
git remote add origin https://github.com/조직명/저장소명.git
```

**예시:**
```bash
git remote add origin https://github.com/TripleC-org/Triple_c_rag.git
```

### 2.4 저장소 내용 가져오기
```bash
# 저장소 정보 가져오기
git fetch origin

# main 브랜치 내용 가져오기
git pull origin main
```

### 2.5 로컬 브랜치와 원격 브랜치 연결
```bash
# 로컬 브랜치 이름을 main으로 변경
git branch -M main

# 원격 브랜치 추적 설정
git branch --set-upstream-to=origin/main main
```

---

## 3. 기존 저장소 클론하는 경우 (더 간단한 방법)

```bash
# 저장소 클론
git clone https://github.com/조직명/저장소명.git

# 폴더로 이동
cd 저장소명
```

**예시:**
```bash
git clone https://github.com/TripleC-org/Triple_c_rag.git
cd Triple_c_rag
```

---

## 4. GitHub에 푸시하기 (상세 가이드)

### 4.1 푸시 전 상태 확인
```bash
# 현재 상태 확인 (어떤 파일이 변경되었는지)
git status
```

**출력 예시:**
```
On branch main
Your branch is up to date with 'origin/main'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        GitHub_연동_가이드.md

nothing added to commit but untracked files present
```

### 4.2 스테이징 (Stage) - 커밋할 파일 선택

```bash
# 모든 변경된 파일 스테이징
git add .

# 또는 특정 파일만 스테이징
git add 파일명.txt

# 또는 특정 폴더만 스테이징
git add src/
```

**스테이징 후 확인:**
```bash
git status
```

**출력 예시:**
```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   GitHub_연동_가이드.md
```

### 4.3 커밋 (Commit) - 변경사항 저장

```bash
# 커밋 메시지와 함께 커밋
git commit -m "커밋 메시지 작성"
```

**좋은 커밋 메시지 예시:**
```bash
git commit -m "feat: GitHub 연동 가이드 문서 추가"
git commit -m "fix: 로그인 버그 수정"
git commit -m "docs: README 업데이트"
```

**커밋 메시지 컨벤션:**
| 태그 | 설명 |
|------|------|
| feat | 새로운 기능 추가 |
| fix | 버그 수정 |
| docs | 문서 수정 |
| style | 코드 포맷팅 (기능 변화 없음) |
| refactor | 코드 리팩토링 |
| test | 테스트 코드 추가 |
| chore | 빌드, 설정 파일 수정 |

### 4.4 푸시 (Push) - GitHub에 업로드

```bash
# main 브랜치에 푸시
git push origin main
```

**출력 예시:**
```
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 2.50 KiB | 2.50 MiB/s, done.
Total 3 (delta 0), reused 0 (delta 0)
To https://github.com/TripleC-org/Triple_c_rag.git
   abc1234..def5678  main -> main
```

### 4.5 한 번에 푸시하기 (요약)

```bash
# 1. 모든 파일 스테이징
git add .

# 2. 커밋
git commit -m "커밋 메시지"

# 3. 푸시
git push origin main
```

**또는 한 줄로:**
```bash
git add . && git commit -m "커밋 메시지" && git push origin main
```

---

## 5. 자주 쓰는 Git 명령어

### 5.1 상태 확인
```bash
# 현재 상태 확인
git status

# 연결된 remote 확인
git remote -v

# 브랜치 확인
git branch -a

# 커밋 히스토리 확인
git log --oneline
```

### 5.2 변경사항 가져오기 (Pull)
```bash
git pull origin main
```

### 5.3 스테이징 취소
```bash
# 특정 파일 스테이징 취소
git restore --staged 파일명

# 모든 파일 스테이징 취소
git restore --staged .
```

### 5.4 마지막 커밋 메시지 수정 (푸시 전에만!)
```bash
git commit --amend -m "새로운 커밋 메시지"
```

---

## 6. 문제 해결

### 6.1 Remote가 이미 존재하는 경우
```bash
# 기존 remote URL 변경
git remote set-url origin https://github.com/조직명/저장소명.git
```

### 6.2 접근 권한 오류

**저장소 쓰기 권한 확인하기:**
```bash
gh repo view 조직명/저장소명 --json viewerPermission
```

**출력 예시:**
```json
{"viewerPermission":"READ"}
```

**권한 종류:**
| 권한 | 설명 |
|------|------|
| READ | 읽기만 가능 (푸시 불가) |
| WRITE | 푸시 가능 |
| ADMIN | 모든 권한 (설정 변경 포함) |

**권한이 READ인 경우:**
- 조직 관리자에게 WRITE 권한 요청
- 또는 권한이 있는 다른 계정으로 전환:
```bash
gh auth switch -u 다른계정이름
```

**현재 로그인된 계정 확인:**
```bash
gh auth status
```

### 6.3 한글 파일명이 이상하게 보이는 경우

```bash
# 변경 전 (유니코드 이스케이프)
GitHub_\354\227\260\353\217\231_\352\260\200\354\235\264\353\223\234.md

# 한글 표시 설정
git config --global core.quotepath false

# 변경 후
GitHub_연동_가이드.md
```

### 6.4 브랜치 충돌
```bash
# 강제로 원격 브랜치 내용으로 덮어쓰기 (주의: 로컬 변경사항 삭제됨)
git fetch origin
git reset --hard origin/main
```

---

## 7. 이번에 수행한 명령어 요약

```bash
# 1. GitHub 로그인 상태 확인
gh auth status

# 2. Remote 저장소 연결
git remote add origin https://github.com/TripleC-org/Triple_c_rag.git

# 3. 저장소 내용 가져오기
git fetch origin
git pull origin main

# 4. 브랜치 설정
git branch -M main
git branch --set-upstream-to=origin/main main
```

---

## 참고 링크

- [GitHub CLI 공식 문서](https://cli.github.com/manual/)
- [Git 공식 문서](https://git-scm.com/doc)
