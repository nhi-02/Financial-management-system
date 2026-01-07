# FinFlow

A modern personal finance management system built with Next.js 14, TypeScript, and Prisma. Designed for home use to manage debts, savings, budgets, investments, and financial goals with intelligent insights and recommendations.

## Features

- 📊 **Transaction Tracking** - Income and expenses with categories
- 💳 **Account Management** - Multiple bank accounts with reconciliation
- 💰 **Debt Management** - Track loans with EMI calculations
- 🎯 **Savings Goals** - Set and monitor savings targets
- 📅 **Budget Planning** - Monthly and yearly budgets
- 📈 **Investment Tracking** - SIP and lump sum investments with returns
- 📉 **Analytics** - Charts and insights with spending trends
- 🧮 **Financial Calculators** - EMI, SIP, Prepay vs Invest
- 💬 **WhatsApp Integration** - Manage finances via WhatsApp (optional)

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes, Prisma ORM
- **Database**: SQLite (easily switchable to PostgreSQL)
- **Charts**: Recharts
- **AI**: Google Gemini Pro (optional for WhatsApp)

## Quick Start

```bash
# Install dependencies
npm install

# Set up database
npm run db:push
npm run db:generate

# Initialize with default data
npm run db:init

# Start development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to access the dashboard

## Data Migration

Import your historical data from Excel:

```bash
# Place HomeBudget.xlsx and LoanDetails.xlsx in project root
npm run db:migrate
```

## Project Structure

```
├── app/                    # Next.js app directory
│   ├── (dashboard)/       # Dashboard pages (transactions, debts, etc.)
│   ├── api/               # API routes (32+ endpoints)
│   └── globals.css        # Global styles
├── components/            # React components
│   └── forms/            # Form components
├── lib/                   # Utilities and helpers
│   ├── calculations.ts   # Financial calculations (EMI, SIP, etc.)
│   ├── decision-engine.ts # Financial recommendations
│   ├── ai-parser.ts      # AI-powered message parsing
│   └── whatsapp-parser.ts # WhatsApp message parsing
├── modules/               # Feature modules (modular monolith)
│   ├── transactions/     # Transaction management
│   ├── debts/           # Debt management
│   ├── savings/         # Savings goals
│   ├── budget/          # Budget management
│   ├── accounts/        # Account management
│   └── investments/     # Investment tracking
├── prisma/               # Database schema and migrations
├── scripts/             # Utility scripts
│   ├── init-db.ts      # Database initialization
│   └── migrate-sheets.ts # Excel data migration
└── shared/              # Shared services
    ├── cache/          # Caching service
    ├── events/         # Event system
    └── queue/          # Background jobs
```

## API Endpoints

### Core Resources
- `/api/transactions` - Transaction CRUD
- `/api/debts` - Debt management
- `/api/savings` - Savings goals
- `/api/budget` - Budget management
- `/api/accounts` - Account management
- `/api/investments` - Investment tracking

### Analytics
- `/api/analytics/spending-trend` - Spending over time
- `/api/analytics/category-breakdown` - Expenses by category
- `/api/analytics/net-worth-trend` - Net worth progression

### Utilities
- `/api/dashboard/stats` - Dashboard statistics
- `/api/advice` - Financial recommendations
- `/api/summary` - Overall financial summary
- `/api/whatsapp/webhook` - WhatsApp integration

## WhatsApp Integration

For WhatsApp integration setup, see [`WHATSAPP_SETUP_GUIDE.md`](./WHATSAPP_SETUP_GUIDE.md).

**Supported Commands**:
```
add expense 500 food lunch
add income 50000 salary
balance
show debts
show savings
how much did I spend on food?
can I afford 20000?
```

## Authentication

**Current**: No authentication (home use, single household)
**Production**: See [`AUTH_IMPLEMENTATION_GUIDE.md`](./AUTH_IMPLEMENTATION_GUIDE.md) for multi-user deployment

## Deployment

### PM2 (Recommended)
```bash
npm run build
pm2 start npm --name "finance-app" -- start
```

### Docker
```bash
docker build -t finance-app .
docker run -p 3000:3000 finance-app
```

## Environment Variables

Create `.env` file:

```bash
# Database (optional, defaults to SQLite)
DATABASE_URL="file:./prisma/finance.db"

# Google Cloud (optional, for AI features)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# NextAuth (optional, for production multi-user)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
```

## Key Features Explained

### Financial Calculators
- **EMI Calculator**: Calculate monthly payments for loans
- **SIP Calculator**: Project investment returns with step-up
- **Prepay Analyzer**: Compare prepayment vs investment returns

### Analytics & Insights
- Spending trends over last 6 months
- Category-wise expense breakdown
- Net worth progression
- Budget vs actual comparison
- Investment returns tracking

### Decision Engine
- Affordability checks
- Debt payoff recommendations (snowball/avalanche)
- Budget alerts
- Savings goal progress
- Financial health score

## Database Schema

Key models:
- `Transaction` - Income/expense records
- `Account` - Bank accounts
- `Debt` - Loans with EMI tracking
- `SavingsGoal` - Savings targets
- `Budget` - Monthly/yearly budgets
- `Investment` - SIP/lump sum investments
- `FinancialYear` - Financial year tracking
- `FinancialAlert` - Automated alerts

## Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run db:generate  # Generate Prisma client
npm run db:push      # Push schema to database
npm run db:init      # Initialize with seed data
npm run db:migrate   # Import Excel data
```

## Development

Built with modular monolith architecture for clean separation of concerns while maintaining simplicity of deployment.

**Architecture**:
- **API Layer**: Next.js API routes
- **Service Layer**: Business logic (modules/*/services)
- **Repository Layer**: Database access (modules/*/repositories)
- **Shared Services**: Cache, events, queue

## Production Considerations

### Security
- ✅ All numeric inputs validated
- ✅ No NaN can enter database
- ✅ XLSX vulnerability patched
- ✅ SQL injection prevention (Prisma)

### Performance
- ✅ Database queries optimized
- ✅ Caching implemented
- ✅ Atomic operations for concurrency
- ✅ Transaction-wrapped deletes

### Data Integrity
- ✅ Comprehensive validation
- ✅ Race condition prevention
- ✅ Atomic increment operations
- ✅ Foreign key constraints

## License

MIT License - Free to use for personal and commercial purposes.

## Support

For issues or questions, check the documentation files:
- `WHATSAPP_SETUP_GUIDE.md` - WhatsApp integration
- `AUTH_IMPLEMENTATION_GUIDE.md` - Multi-user authentication

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Build**: ✅ Successful (0 errors, 0 warnings)

Made with ❤️ for better financial management.

# 💰 Ứng dụng Quản lý Tiết kiệm

Ứng dụng đơn giản để theo dõi các mục tiêu tiết kiệm cá nhân.

## Yêu cầu

- Python 3.8+
- SQLite3

## Cài đặt

```bash
# Cài dependencies
pip install -r requirements.txt

# Tạo database (nếu chưa có)
# Database sử dụng Prisma schema có sẵn tại prisma/schema.prisma
```

## Chạy ứng dụng

```bash
python app.py
```

Mở trình duyệt: http://localhost:5000

## Tính năng

- ✅ Tạo mục tiêu tiết kiệm
- ✅ Theo dõi tiến độ
- ✅ Cập nhật số tiền đã tiết kiệm
- ✅ Xóa mục tiêu

## Cấu trúc

```
finflow/
├── app.py              # Flask app chính
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── new_goal.html
│   └── edit_goal.html
├── static/
│   └── style.css       # CSS
├── prisma/
│   ├── schema.prisma   # Database schema
│   └── dev.db          # SQLite database
└── requirements.txt
```

## License

MIT

# FinFlow (Python Flask) — Quick Start

FinFlow là ứng dụng quản lý tiết kiệm cá nhân bằng Python + Flask và SQLite (nhẹ, chạy local).

## Yêu cầu
- Python 3.8+
- SQLite3

## Cài đặt
1. Tạo virtualenv (khuyến nghị)
```sh
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Cài dependencies
```sh
pip install -r requirements.txt
```

## Tạo và khởi tạo database (local)
- Script khởi tạo schema: [`init_db.init_database`](init_db.py)
```sh
python init_db.py
```
- Mặc định db file: `prisma/dev.db`. Nếu muốn đổi, sửa đường dẫn trong [`models.Database.__init__`](models.py) hoặc [`init_db.py`](init_db.py).

## Chạy ứng dụng
```sh
python app.py
```
Truy cập: http://localhost:5000

## Các route chính
- Trang chủ (Dashboard): `/` — route: [`app.index`](app.py)
- Tạo mục tiêu: `/goal/new` — template: [`templates/new_goal.html`](templates/new_goal.html)
- Danh sách tài khoản: `/accounts` — template: [`templates/accounts.html`](templates/accounts.html)
- API danh sách mục tiêu (JSON): `/api/goals` — dùng [`services.SavingsService.get_summary`](services.py)

## Thay đổi dữ liệu / debug
- Model / DB helpers: [`models.Database`](models.py)
- Business logic: [`services.SavingsService`](services.py), [`services.AccountService`](services.py)
- Đổi schema (Prisma): [`prisma/schema.prisma`](prisma/schema.prisma) — lưu ý: Prisma file chỉ để tham khảo; Flask app dùng SQLite trực tiếp.

## Giao diện & tĩnh
- Templates: `templates/` (VD: [`templates/index.html`](templates/index.html), [`templates/base.html`](templates/base.html))
- Static: `static/style.css`, `static/script.js`

## Lưu ý
- Nếu nhận cảnh báo "Database chưa tồn tại", kiểm tra file `prisma/dev.db` và chạy `python init_db.py`.
- Nếu template gọi một endpoint không tồn tại (ví dụ `accounts_list`), đảm bảo route tương ứng có trong [`app.py`](app.py).

## Thêm chức năng (gợi ý)
- Thêm auth (register/login) → tạo bảng User trong `init_db.py` và model trong `models.py`.
- Nếu muốn đổi tên DB file sang `prisma/finance.db`, cập nhật cả `init_db.py` và `models.py`.

## Tập tin chính
- [`app.py`](app.py) — Flask app và routes
- [`init_db.py`](init_db.py) — tạo schema & seed cơ bản
- [`models.py`](models.py) — lớp Database, `SavingsGoal`, `Account`, `Transaction`
- [`services.py`](services.py) — logic nghiệp vụ (Savings, Account, Transaction)
- [`utils.py`](utils.py) — helpers (format tiền / ngày)
