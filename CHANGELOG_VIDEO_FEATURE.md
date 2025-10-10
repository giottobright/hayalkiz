# Changelog - Video Generation Feature

## [2.1.0] - 2025-10-10

### 🎬 Added - Video Generation Feature

#### New Services
- **`services_sora.py`** - Sora 2 API integration
  - `SoraService` class with async video generation
  - Support for image-to-video and text-to-video modes
  - Polling mechanism for async task completion
  - Error handling and retry logic

#### Enhanced Services
- **`services_gpt.py`**
  - Added `build_video_prompt()` method
  - Generates Sora 2-compliant video prompts from photo prompts
  - 50% chance of adding seductive/flirty elements
  - Follows Sora 2 best practices from official documentation

#### Database Updates
- **`db.py`**
  - New table `generated_content` for storing prompts and media
  - `save_generated_content()` - save selfies and videos with prompts
  - `get_last_selfie_prompt()` - retrieve last selfie prompt
  - `get_last_selfie_data()` - retrieve last selfie prompt and image bytes

#### Bot Features
- **`main.py`**
  - New button "🎬 Video gönder" / "🎬 Отправь видео"
  - `video_choice_keyboard()` - inline keyboard for video mode selection
  - `ask_video_mode()` - prompt user to choose video generation mode
  - `generate_video_from_selfie()` - create video from last selfie
  - `generate_new_video()` - create video from scratch (selfie + video)
  - Callback handler `on_video_mode()` for video mode selection
  - Updated `generate_selfie()` to save prompts to database
  - Video request detection in message handler

### 📝 Video Generation Modes

#### Mode 1: Video from Selfie
1. User creates selfie
2. User requests video
3. System retrieves last selfie prompt
4. GPT generates video prompt from selfie prompt
5. Sora 2 generates 5-second video using selfie as reference

**Time**: ~30-60 seconds

#### Mode 2: New Video
1. User requests new video
2. System generates new selfie prompt (GPT)
3. System generates selfie image (Gemini)
4. GPT generates video prompt from selfie prompt
5. Sora 2 generates 5-second video using new selfie

**Time**: ~60-120 seconds

### 🎥 Video Specifications

- **Duration**: 5 seconds (configurable: 4, 8, or 12)
- **Resolution**: 720x1280 (vertical HD)
- **Format**: MP4
- **Size**: 5-20 MB per video
- **Quality**: Cinematic, iPhone-quality
- **Model**: Sora 2 (upgradeable to Sora 2 Pro)

### 🎨 Content Variety

- **Regular videos**: Girl smiles, makes gentle gestures, shows personality
- **Seductive videos** (50% chance): Flirty camera interaction, playful eye contact, inviting gestures, tasteful skin exposure

### 📚 Documentation

- **`VIDEO_FEATURE_GUIDE.md`** - Complete technical guide (English)
- **`VIDEO_USER_GUIDE_RU_TR.md`** - User guide (Russian/Turkish)

### 🔧 Configuration

Uses existing `OPENAI_API_KEY` from `back/keys.env` for both GPT and Sora 2 API calls.

### 🌐 Localization

Full support for Turkish and Russian languages:
- Button labels
- Status messages
- Error messages
- Success messages

### 🔐 Security

- Prompts and content stored in local SQLite database
- API keys stored in environment file (not committed)
- Video files stored as BLOB in database (optional)

### ⚡ Performance

- Async/await throughout for non-blocking operations
- Efficient database queries with proper indexing
- Polling with timeout protection (max 120 attempts)
- Graceful error handling and fallbacks

### 🐛 Bug Fixes

None - this is a new feature

### 🚀 Technical Implementation

#### Sora 2 Prompt Structure

Following official Sora 2 guidelines:
1. **Style & Format** (1-2 sentences)
2. **Scene description** with location, lighting, atmosphere (2-3 sentences)
3. **Cinematography**: camera shot, lens, lighting setup, mood (2-3 sentences)
4. **Actions**: ONE clear movement over 5 seconds
5. **Background Sound**: ambient only, no music

Total: 8-12 sentences per prompt

#### Example Flow

```
User: [Presses "🎬 Video gönder"]
Bot: [Shows inline keyboard with 2 options]
User: [Selects "📸➡️🎬 Video from last selfie"]
Bot: "🎬 Генерирую видео..."
     [Retrieves last selfie prompt]
     [GPT generates video prompt]
     [Shows debug info with prompts]
     [Sora 2 generates video]
     "Вот моё видео! 🎥💕"
     [Sends video file]
```

### 📊 Database Schema

```sql
CREATE TABLE generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    content_type TEXT,  -- 'selfie' or 'video'
    prompt TEXT,
    file_data BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 🔄 API Integration

#### Sora 2 API Endpoints

- **POST** `https://api.openai.com/v1/video/generations` - Create video
- **GET** `https://api.openai.com/v1/video/generations/{id}` - Poll status

#### Request Parameters

```json
{
  "model": "sora-2",
  "prompt": "...",
  "size": "720x1280",
  "seconds": "5",
  "image": "data:image/png;base64,..."  // optional
}
```

#### Response Polling

System polls every 2 seconds until:
- Status: `completed` → Download video
- Status: `failed` → Show error
- Timeout: 120 attempts (~4 minutes)

### 🎯 Future Enhancements

- [ ] Multiple duration options in UI
- [ ] Different video styles (documentary, cinematic, etc)
- [ ] Preview frame before generation
- [ ] Video history and gallery
- [ ] Export to external storage (S3)
- [ ] Multi-scene transitions
- [ ] Custom seductive probability per user
- [ ] Video editing (trim, filters)

### 🙏 Credits

- **Sora 2 API**: OpenAI
- **Prompt engineering**: Based on official Sora 2 prompting guide
- **Architecture**: Built on existing HayalKiz bot infrastructure

---

## Installation / Update Instructions

### For existing deployments:

1. **Pull latest code**:
   ```bash
   git pull origin main
   ```

2. **Database will auto-migrate** on first run (new table created automatically)

3. **No new environment variables needed** (uses existing `OPENAI_API_KEY`)

4. **Restart bot**:
   ```bash
   cd back
   python start.py
   # or
   docker-compose restart
   ```

5. **Test**:
   - Open bot in Telegram
   - Select a girl
   - Click "🎬 Video gönder"
   - Choose video mode
   - Wait for video generation

### Requirements:

- `OPENAI_API_KEY` must have access to Sora 2 API (currently in beta)
- Sufficient OpenAI credits for video generation
- Stable internet connection for API calls

---

## Known Issues

None at this time.

## Breaking Changes

None - fully backward compatible with existing features.

---

**Version**: 2.1.0  
**Date**: October 10, 2025  
**Author**: HayalKiz Development Team



