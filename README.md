# DeadlineSnap 📅

An AI-powered deadline tracker that helps students stay organized. Upload photos of your syllabus, type deadlines directly, and get a clean digest with calendar integration.

## Features

- 📸 **Photo Upload**: Take pictures of syllabi, timetables, and assignment sheets
- 💬 **Chat Interface**: Natural conversation with AI to extract deadlines
- 📧 **Email Digest**: Get a summary of your deadlines with a calendar file
- 📅 **Calendar Integration**: .ics files for Google/Apple/Outlook Calendar
- 🎯 **Urgency Tracking**: Visual indicators for upcoming deadlines
- 📊 **Study Planning**: Automatic study session scheduling
- 🔍 **Smart Extraction**: Accurate date and deadline extraction from images
- ✏️ **Editable Deadlines**: Review and edit extracted information

## Tech Stack

- **Frontend**: Streamlit
- **AI**: Google Gemini 3.5 Flash (Vision + Chat)
- **Email**: Gmail SMTP
- **Calendar**: iCalendar (.ics) format
- **Language**: Python 3.9+

## Project Structure

```
deadlinesnap/
├── app.py              # Main Streamlit application
├── core.py             # Core logic and utilities
├── prompts.py         # AI prompts and templates
├── requirements.txt   # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore rules
└── .streamlit/
    └── secrets.toml.example  # Template for secrets
```

## Setup Instructions

### 1. Get API Keys

- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Gmail App Password**: 
  1. Enable 2-Step Verification on your Google account
  2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
  3. Select "Mail" and "Other (Custom name)" - name it "DeadlineSnap"
  4. Generate and copy the 16-character password

### 2. Local Development

#### macOS/Linux
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Copy secrets template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit the file with your actual keys

# Run app
streamlit run app.py
```

#### Windows PowerShell
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Copy secrets template
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
# Edit the file with your actual keys

# Run app
streamlit run app.py
```

### 3. Streamlit Community Cloud Deployment

1. **Push to GitHub** (without `.streamlit/secrets.toml`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repository
5. Select `app.py` as the main file
6. Go to "Settings" > "Secrets" and add:
   - `GEMINI_API_KEY`
   - `GMAIL_ADDRESS`
   - `GMAIL_APP_PASSWORD`

## How It Works

### Prompt Design
The system prompt is tightly scoped to deadline extraction only:
- Extracts dates, times, and titles from academic documents
- Never invents dates - asks for clarification when unclear
- Handles missing years by assuming the nearest upcoming occurrence
- Uses Asia/Kolkata timezone (IST) as default

### Core Flow
1. **Onboarding**: User enters name and email
2. **Chat**: Upload images or type text to extract deadlines
3. **Review**: Edit extracted information in a table
4. **Export**: Email digest + calendar file

### Safety & Privacy
- Photos and emails are not stored - everything lives in the session only
- No real secrets are committed to the repository
- Graceful handling of AI errors and invalid inputs

## Known Limitations

- **Handwriting Accuracy**: Works best with clear, typed text
- **Image Quality**: Blurry or poorly lit photos may not extract well
- **Timezone**: Defaults to Asia/Kolkata (IST)
- **Gmail Requirement**: Needs Gmail with App Password authentication
- **Date Parsing**: May struggle with ambiguous date formats

## Ideas for Future Work

- Support for multiple calendar formats (.ics, .csv)
- Integration with popular calendar apps
- Mobile app companion
- Deadline notifications via email/SMS
- Support for handwritten notes (OCR)
- Multi-language support
- Dark/light theme toggle
- Export to project management tools (Trello, Asana)

## Design Decisions

### Human-in-the-Loop Review
- Students need to verify extracted information
- Academic deadlines are critical - errors can have serious consequences
- Allows manual correction of AI mistakes

### Gmail SMTP
- Simple and reliable for most students
- No additional dependencies beyond standard library
- Widely accessible email service

### Core Logic Separation
- `core.py` contains pure functions for easy testing
- UI logic stays in `app.py`
- Prompts separated in `prompts.py` for easy iteration

## Testing

Before deploying, run these tests:

```bash
# Check syntax
python -c "import ast,sys; ast.parse(open('app.py').read())"
python -c "import ast,sys; ast.parse(open('prompts.py').read())"
python -c "import ast,sys; ast.parse(open('core.py').read())"

# Test core functions (create a test script)
python -m pytest tests/test_core.py

# Start app headless
streamlit run app.py --server.headless true
```

## License

This project is for educational purposes.