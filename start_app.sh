#!/bin/bash

while IFS='=' read -r key value; do
  if [[ $key == START_* ]]; then
    export "$key=$value"
  fi
done < .env


echo "🚀 Démarrage des services..."

# # --- Uvicorn API ---
echo "⚙️  Démarrage de l'API Uvicorn..."
cd "$START_PROJECT_DIR/api" || exit 1
uvicorn main:app --reload --host 0.0.0.0 --port $START_PORT_FASTAPI_LOCAL &
UVICORN_PID=$!

sleep 2

# # --- Streamlit ---
echo "🌐 Démarrage de Streamlit..."
cd "$START_PROJECT_DIR" || exit 1
streamlit run $START_STREAMLIT_PATH &
STREAMLIT_PID=$!

echo ""
echo "✅ Tous les services sont lancés :"
echo "   Streamlit        → PORT          → PID $STREAMLIT_PID"
echo "   Uvicorn API      → PORT $START_PORT_FASTAPI_LOCAL      → PID $UVICORN_PID"
echo ""
echo "💡 Pour tout arrêter : Ctrl+C"

# # Garder le script actif et intercepter Ctrl+C pour tout arrêter proprement
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    kill $STREAMLIT_PID $UVICORN_PID 2>/dev/null           
    wait $STREAMLIT_PID $UVICORN_PID 2>/dev/null           
    echo "✅ Tous les services arrêtés."
    exit 0
}

trap cleanup SIGINT SIGTERM


wait