#!/bin/bash
echo "========== Vue Blog 启动脚本 =========="

echo ""
echo "[1] 安装前端依赖..."
cd "$(dirname "$0")"
npm install

echo ""
echo "[2] 安装后端依赖..."
cd "$(dirname "$0")/backend"
pip install -r requirements.txt

echo ""
echo "[3] 初始化后端数据库..."
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"

echo ""
echo "========== 启动完成 =========="
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8000"
echo ""
echo "管理员账号: admin / admin123"
echo ""
echo "启动命令:"
echo "  前端: npm run dev"
echo "  后端: cd backend && python main.py"
