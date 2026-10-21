install-backend:
	cd backend && pip install -r requirements.txt
install-frontend:
	cd frontend && npm install
test:
	cd backend && pytest -q
run-backend:
	cd backend && uvicorn app.main:app --reload
run-frontend:
	cd frontend && npm run dev
