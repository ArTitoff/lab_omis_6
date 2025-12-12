from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("Система умного планирования расписания")
    print("Сервер запущен на http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
