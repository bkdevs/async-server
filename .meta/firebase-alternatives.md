# Firebase Alternatives for Async-Server

This document outlines drop-in replacements for Firebase in the async-server application, including local development options and production alternatives.

## Current Firebase Usage

The async-server application uses Firebase as its primary backend infrastructure:

### Services Used
- **Firestore Database**: NoSQL document database for all application data
- **Firebase Storage**: File storage for project images
- **Firebase Admin SDK**: Service account authentication

### Data Storage Structure
```
Collections:
├── users/                          # User accounts, GitHub info, Stripe IDs
├── orgs/                          # Organizations, payment plans, credits
│   └── {orgId}/profiles/          # User profiles within organizations
│   └── {orgId}/projects/          # Development projects, repo info
│   └── {orgId}/tasks/             # AI development tasks
│       └── {taskId}/subtasks/     # AI-generated implementation steps
│       └── {taskId}/messages/     # Chat conversations with AI
├── repos/                         # GitHub repository metadata
├── prs/                          # Pull request tracking
├── email_codes/                  # Email verification codes
├── invites/                      # Team invitation management
├── stripe/                       # Payment customer records
├── slack/                        # Slack integration data
└── leads/                        # Sales/support leads

Storage:
└── orgs/{orgId}/projects/{projectId}/image.webp
```

## Local Development Alternatives

### 1. Firebase Emulator Suite (Recommended)

**Perfect drop-in replacement requiring zero code changes.**

#### Setup
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Create firebase.json in project root
cat > firebase.json << EOF
{
  "emulators": {
    "firestore": {
      "port": 8080
    },
    "storage": {
      "port": 9199
    }
  }
}
EOF

# Start emulators
firebase emulators:start
```

#### Configuration
```bash
# Set environment variables before running the app
export FIRESTORE_EMULATOR_HOST=localhost:8080
export FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199

# Use the same async-firebase.json file (emulator ignores auth)
# Start the application normally
uvicorn src.server:app --reload --port 8000
```

#### Advantages
- ✅ **Zero code changes** required
- ✅ Same Firebase SDK and API
- ✅ Local web UI at http://localhost:4000 for data inspection
- ✅ Fast development and testing
- ✅ Data persistence between restarts (optional)
- ✅ Import/export data functionality

#### Disadvantages
- ⚠️ Requires Node.js and Firebase CLI
- ⚠️ Additional local service to manage

### 2. MongoDB + MinIO

**Self-hosted alternative with Docker.**

#### Setup
```bash
# Start MongoDB
docker run -d --name mongo \
  -p 27017:27017 \
  -v mongo_data:/data/db \
  mongo:latest

# Start MinIO (S3-compatible storage)
docker run -d --name minio \
  -p 9000:9000 -p 9001:9001 \
  -v minio_data:/data \
  minio/minio server /data --console-address ":9001"
```

#### Code Changes Required
- Replace `FirestoreClient` with MongoDB client
- Replace `StorageClient` with MinIO/S3 client
- Update all database operations to use MongoDB syntax
- Significant refactoring of `src/firebase/` directory

#### Advantages
- ✅ Completely self-hosted
- ✅ No external dependencies
- ✅ Production-ready components

#### Disadvantages
- ❌ Requires extensive code modifications
- ❌ Different query syntax and data modeling
- ❌ Loss of Firestore's real-time features

## Production Alternatives

### 1. Supabase (Most Similar to Firebase)

**PostgreSQL-based Firebase alternative with similar features.**

#### Setup
```bash
# Create Supabase project at https://supabase.com
# Get project URL and anon key from dashboard
```

#### Code Changes Required
- Install Supabase client: `pip install supabase`
- Replace Firebase imports with Supabase client
- Adapt Firestore document operations to PostgreSQL tables
- Migrate storage operations to Supabase Storage

#### Migration Steps
```python
# Replace this:
from firebase_admin import firestore
client = firestore_async.client()

# With this:
from supabase import create_client
client = create_client(supabase_url, supabase_key)
```

#### Advantages
- ✅ Real-time subscriptions
- ✅ Built-in authentication
- ✅ File storage included
- ✅ PostgreSQL reliability
- ✅ Generous free tier

#### Disadvantages
- ❌ Different API requiring code changes
- ❌ SQL-based instead of NoSQL
- ❌ Learning curve for team

### 2. PlanetScale + Cloudflare R2

**Serverless MySQL database + S3-compatible storage.**

#### Services
- **PlanetScale**: Serverless MySQL with branching
- **Cloudflare R2**: S3-compatible object storage

#### Code Changes Required
- Replace Firestore with SQL ORM (SQLAlchemy)
- Convert document operations to relational queries
- Replace Firebase Storage with R2 SDK

#### Advantages
- ✅ Serverless and scalable
- ✅ SQL ACID compliance
- ✅ Great developer experience
- ✅ Cost-effective

#### Disadvantages
- ❌ Complete architecture change
- ❌ Requires database schema design
- ❌ No real-time features

### 3. Railway + PostgreSQL

**Simple hosting platform with managed PostgreSQL.**

#### Setup
```bash
# Deploy to Railway with PostgreSQL addon
# Get database connection string from Railway dashboard
```

#### Code Changes Required
- Similar to Supabase but with raw PostgreSQL
- Implement custom real-time features if needed
- Add file storage solution (AWS S3, etc.)

#### Advantages
- ✅ Simple deployment
- ✅ Managed PostgreSQL
- ✅ Good pricing
- ✅ Git-based deployments

#### Disadvantages
- ❌ Requires significant refactoring
- ❌ No built-in real-time features
- ❌ Separate file storage needed

## Recommendations

### For Local Development
**Use Firebase Emulator Suite** - it provides the fastest path to local development:

1. No code changes required
2. Same APIs and behavior as production Firebase
3. Easy data inspection and management
4. Can be set up in under 5 minutes

### For Production Migration
**Consider your priorities:**

- **Minimal Code Changes**: Stay with Firebase but switch to production mode
- **Open Source**: Supabase offers the closest feature parity
- **Enterprise**: PlanetScale + dedicated storage for reliability
- **Simplicity**: Railway + PostgreSQL for straightforward hosting

### Implementation Timeline

#### Phase 1: Local Development (Immediate)
```bash
# Set up Firebase Emulator Suite
npm install -g firebase-tools
firebase init emulators
firebase emulators:start
```

#### Phase 2: Production Decision (Before deploying)
1. Evaluate data requirements and team expertise
2. Choose between staying with Firebase vs. migration
3. Plan migration strategy if moving away from Firebase

#### Phase 3: Migration (If applicable)
1. Set up new infrastructure
2. Create data migration scripts
3. Update application code incrementally
4. Test thoroughly before switching

## Security Considerations

### Firebase Emulator Suite
- Local emulators bypass authentication
- Safe for development but never expose emulator ports publicly
- Data is stored locally and not encrypted

### Production Alternatives
- All alternatives require proper authentication setup
- Implement proper security rules/policies
- Use environment variables for sensitive credentials
- Enable encryption at rest and in transit

## Cost Comparison

### Firebase (Current)
- Free tier: 1GB storage, 50k reads/day
- Pay-as-you-go pricing
- Automatic scaling

### Supabase
- Free tier: 500MB database, 1GB storage
- Pro plan: $25/month for larger limits
- Predictable pricing

### PlanetScale + R2
- PlanetScale: Free tier, then usage-based
- R2: $0.015/GB storage, very low egress costs
- Cost-effective for high-traffic applications

### Self-Hosted
- Infrastructure costs only
- Requires operational overhead
- Most cost-effective at scale

## Conclusion

For immediate local development, **Firebase Emulator Suite** is the clear winner, requiring zero code changes and providing a perfect development environment.

For production, the choice depends on your specific needs:
- **Stay with Firebase** if you want minimal changes and are comfortable with Google Cloud Platform
- **Choose Supabase** if you want Firebase-like features with more control
- **Go with PlanetScale + R2** if you need enterprise-grade reliability and SQL
- **Use self-hosted solutions** if you require complete control and have operational expertise

The async-server application's heavy reliance on Firestore's document model and Firebase Storage makes the emulator suite the most practical choice for local development, while production decisions should be based on long-term architectural goals and team capabilities.
