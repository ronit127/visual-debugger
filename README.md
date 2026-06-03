# Visual Debugger

## Setup

### 1. Clone and install frontend dependencies

```bash
npm install
```

### 2. Install backend dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env.local` file in the project root:

```env
# Google OAuth — https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here

# NextAuth secret — generate with: openssl rand -base64 32
AUTH_SECRET=your_auth_secret_here

# Flask backend URL (default shown)
FLASK_API_URL=http://localhost:5000
```

## Running the Project

Open two terminals:

**Terminal 1 — Frontend**
```bash
npm run dev
# Runs on http://localhost:3000
```

**Terminal 2 — Backend**
```bash
cd backend
source .venv/bin/activate
python app.py
# Runs on http://localhost:5000
```

Then open [http://localhost:3000](http://localhost:3000)

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create an OAuth 2.0 Web Application credential
3. Add `http://localhost:3000` as an authorized JavaScript origin
4. Add `http://localhost:3000/api/auth/callback/google` as an authorized redirect URI
5. Copy the Client ID and Client Secret into your `.env.local`
