#!/bin/sh
# HomePick/backend/entrypoint.sh (수정)

# ... (DB 연결 대기 로직 생략) ...

echo "PostgreSQL started successfully!"

# 1. 초기 DB 마이그레이션 적용 (구조 구축)
echo "Applying migrations..."
python manage.py makemigrations 
python manage.py migrate --no-input

# 2. 초기 데이터 로드 추가 (데이터 구축)
if [ -f "initial_data.json" ]; then # 파일이 존재하는지 확인
  echo "Loading initial data fixtures..."
  python manage.py loaddata initial_data.json
else
  echo "No initial data fixture found. Skipping data loading."
fi

# 이후 CMD 명령(runserver) 실행
exec "$@"
