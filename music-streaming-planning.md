# Self-Hosted Music/Podcast Streaming Service - Planning Document

## Document Info
- **Version:** 3.0
- **Date:** 2026-02-06
- **Status:** Planning Phase (Python Stack Confirmed)
- **Architecture Style:** Monolith with File-Based Storage

---

## 1. Executive Summary

A self-hosted music and podcast streaming platform leveraging YouTube as the content source via yt-dlp Python API. The platform enables users to search, stream audio-only content, and discover related videos through a web interface.

**Key Technology Decisions (v3.0):**
- **Server:** Python + FastAPI (not Go)
- **Why Python:** yt-dlp is Python-native (direct API access), faster MVP development, easier metadata parsing, cleaner Docker image
- **Client:** Vanilla JS + HTML5 Audio (no YouTube iframe)
- **Audio Streaming:** Client streams directly from YouTube CDN (server never proxies audio)

---

## 2. API Contract

### 2.1 Resolve Endpoint

```python
POST /resolve
Request Body:
{
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
}

Response:
{
  "id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "duration": 213,
  "audio_url": "https://rrX---sn-xxxxx-xxxx.googlevideo.com/...",
  "related": [
    {
      "id": "another_video_id",
      "title": "Related Track Title",
      "duration": 198
    },
    ...
  ]
}
```

**Constraints:**
- `related_videos` is **best-effort** (may be empty, order may differ from YouTube UI)
- Audio-only: `audio_url` is direct CDN stream, not YouTube embed
- Server only resolves metadata + stream URL (no audio proxying)

---

## 2.1 Updated Functional Requirements (As Tests)

```
TEST-006: Related Videos
Given a user is viewing a track
When they access related content
Then they see YouTube-related videos fetched via yt-dlp

TEST-007: Gapless Playback
Given a user is playing a track
When T-15 seconds remain in the current track
Then the browser pre-fetches the next track URL (provided by API)
And playback transitions seamlessly without interruption

TEST-008: Repeat Track
Given repeat track mode is enabled
When the current track ends
Then it restarts from the beginning

TEST-009: Repeat Playlist
Given repeat playlist mode is enabled
When the last track ends
Then playback restarts from the first track

TEST-010: Persistent Volume
Given a user has set their volume preference
When they return to the platform
Then their volume setting is restored

TEST-011: Track Removed Handling
Given a track in a playing playlist is removed
When playback reaches that position
Then it skips to the next available track

TEST-012: Region Blocked Content
Given a user attempts to play region-restricted content
When YouTube blocks the stream
Then an appropriate error message is displayed

TEST-013: Android Share Integration
Given a user views content on an Android browser
When they use the native share button
Then shareable links are available via the Android share intent

TEST-014: Public Playlist Discovery
Given a user visits the playlist discovery page
When they search/browse public playlists
Then they find playlists marked as public
(separate from main search results)

TEST-015: Playlist Search
Given a user searches for playlists
When they enter a query
Then results include matching user playlists (public only)
```

### 2.2 Updated Technical Constraints (As Tests)

```
TEST-TC-004: No Offline Mode
Given any user interaction
When accessing content
Then all streaming requires active network connection

TEST-TC-005: No File Modification
Given a track is streaming
When users interact with the platform
Then the streaming file cannot be changed or saved locally

TEST-TC-006: yt-dlp Bundled
Given the project structure
When the service runs
Then yt-dlp is bundled within the project directory (not external)

TEST-TC-007: Playlist Metadata Cache
Given playlist metadata is retrieved
When cached data exists
Then cached metadata is valid for 1 day (1440 minutes)

TEST-TC-008: File Size Limit
Given a file is uploaded or created
When the file exceeds 2 MB
Then the operation is rejected with appropriate error
```

### 2.1 Functional Requirements (As Tests)

```
TEST-001: Content Discovery
Given a user visits the homepage
When they search for "relaxing piano"
Then they see matching music/podcast results from YouTube

TEST-002: Playlist Creation
Given an authenticated user
When they create a new playlist named "Morning Commute"
Then the playlist is saved to their user profile as JSON

TEST-003: Playlist Sharing
Given a user has a playlist
When they click "Share"
Then a shareable link is generated showing song names in order

TEST-004: Content Playback
Given a user clicks play on a track
When the track begins streaming
Then audio plays without pre-resolving URLs or caching stream links

TEST-005: Concurrent Users
When 1000 users simultaneously stream content
Then all streams remain responsive (<2s buffer)
```

### 2.2 Non-Functional Requirements (As Tests)

```
TEST-NF-001: Latency
Given any user action (search, play, create playlist)
When measured from request to response
Then latency remains under 500ms for 99th percentile

TEST-NF-002: Availability
Given the server is running
When users access the platform
Then uptime remains at 99.5% or higher

TEST-NF-003: Scalability
Given 1000 concurrent users streaming
When monitoring resource usage
Then CPU stays under 70%, memory under 80%
```

### 2.3 Technical Constraints (As Tests)

```
TEST-TC-001: No Pre-resolution
Given a playlist exists in the system
When checking for streaming availability
Then no URLs are pre-resolved or cached

TEST-TC-002: No Database
Given the system is operational
When checking storage mechanisms
Then only JSON files and in-memory structures are used

TEST-TC-003: YouTube Only
Given a content request
When searching or resolving
Then content is sourced exclusively from YouTube via yt-dlp
```

---

## 3. Green Phase: Minimal Implementation Vision

### 3.1 Core Loop (Pseudocode)

```python
# Minimal viable streaming flow
def stream_track(video_id):
    # Just-in-time resolution - never cache
    stream_url = yt_dlp.extract_info(video_id, download=False)
    player.play(stream_url['url'])
    # Discard after playback

def create_playlist(user_id, name, video_ids):
    # Store metadata only
    playlist = {
        'id': generate_uuid(),
        'name': name,
        'user_id': user_id,
        'tracks': [{'id': vid, 'title': None, 'duration': None}],
        'created_at': now()
    }
    save_to_json(f"playlists/{playlist['id']}.json", playlist)

def search_content(query):
    # Resolve titles just-in-time for display
    return yt_dlp.search(query, limit=20)
```

### 3.2 Minimal Viable Features

1. **Homepage:** Search bar + featured/curated playlists
2. **Search:** YouTube search results with basic metadata
3. **Player:** HTML5 audio/video player with play/pause/seek
4. **Playlists:** Create, edit, delete, share (authenticated)
5. **Sharing:** Public link generation for playlists
6. **Auth:** Simple session-based authentication (optional)

---

## 4. Blue Phase: Refactored Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Web Browser │  │ Mobile Web  │  │  Desktop Browser         │ │
│  │  (Primary)   │  │  (Responsive)│  │  (Full Feature)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   MONOLITH SERVER                            ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐  ││
│  │  │  REST API │ │  Auth    │ │ yt-dlp   │ │ Static Assets   │  ││
│  │  │  Layer    │ │ Service  │ │ Wrapper  │ │ (HTML/CSS/JS)   │  ││
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  File System     │  │  In-Memory Cache │  │  YouTube API     │ │
│  │  (JSON Playlists)│  │  (Session Data)  │  │  (yt-dlp)        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Breakdown

#### 4.2.1 Web Frontend
**Technology:** Vanilla JS + HTML5 Audio/Video
**Responsibilities:**
- Single-page application for dynamic interactions
- YouTube IFrame embeds or HTML5 audio elements
- Responsive design for mobile/desktop
- Playlist management UI
- Gapless playback pre-fetch logic (T-15s)
- Repeat mode toggles (track/playlist/none)
- Persistent volume management
- Android native share integration (Web Share API)
- Region blocked error handling UI

**Gapless Playback Implementation:**
```javascript
// Client-side pre-fetch logic
player.on('timeupdate', () => {
  const remaining = player.duration - player.currentTime;
  if (remaining <= 15 && !prefetching && nextTrackUrl) {
    prefetching = true;
    // Browser pre-fetches, doesn't play yet
    player.preload = 'metadata';  // or fetch and cache in memory
  }
});

player.on('ended', () => {
  if (repeatMode === 'track') {
    player.currentTime = 0;
    player.play();
  } else if (nextTrackUrl) {
    player.src = nextTrackUrl;
    player.play();
  }
  // For repeat playlist, after last track → loop to first
});
```

**Android Share Integration:**
```javascript
async function shareContent(title, url) {
  if (navigator.share) {
    // Native Android share button
    await navigator.share({
      title: title,
      text: 'Check out this music!',
      url: url
    });
  } else {
    // Fallback: Copy to clipboard
    navigator.clipboard.writeText(url);
  }
}
```

#### 4.2.2 REST API Server
**Technology:** Go (Golang) for concurrency or Node.js
**Responsibilities:**
- HTTP request handling
- Session management
- Playlist CRUD operations
- Search orchestration
- Rate limiting

#### 4.2.3 YouTube Integration Layer
**Technology:** yt-dlp (bundled in project)
**Responsibilities:**
- Video metadata extraction
- Stream URL resolution (just-in-time)
- Search functionality (tracks and playlists)
- Related videos extraction
- Format selection (HLS/DASH preference)
- Bundled binary: `./yt-dlp` or embedded library

**Bundling Strategy:**
```
├── yt-dlp/
│   ├── yt-dlp              # Pre-built binary (Linux/macOS/Windows)
│   └── requirements.txt    # Python dependencies (if using Python wrapper)
```

#### 4.2.4 Storage Manager
**Technology:** File system + In-memory
**Responsibilities:**
- JSON playlist persistence
- Session storage
- Search result caching (short TTL)
- Playlist metadata caching (1-day TTL)
- User preferences (volume, repeat mode)
- Enforce 2MB file size limit on uploads

**Caching Strategy:**
```
Cache Type              TTL          Invalidated When
────────────────────────────────────────────────────────
Playlist Metadata       1 day        Playlist modified
Search Results          5 minutes    Query differs
User Preferences         Persistent   User updates settings
Session Data             24 hours     Session expires
```

### 4.3 Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER ACTIONS & DATA FLOW                        │
└────────────────────────────────────────────────────────────────────────┘

1. SEARCH FLOW
─────────────
   User: Enter search query
        │
        ▼
   API: Receive query
        │
        ▼
   yt-dlp: Search YouTube
        │
        ▼
   Cache: Store results (5-min TTL)
        │
        ▼
   API: Return metadata (titles, IDs, durations)
        │
        ▼
   Frontend: Display search results

2. STREAMING FLOW (Gapless)
───────────────────────────
   User: Click "Play" on track
        │
        ▼
   API: Validate track ID (no URL resolution)
        │
        ▼
   yt-dlp: Extract stream URL (just-in-time)
        │
        ▼
   Frontend: Direct stream to player
        │
        ├──→ Track starts playing
        │
        ├──→ Client requests NEXT track URL (T-15s before end)
        │    GET /api/tracks/{next_track_id}/stream
        │    Returns: { current_url, next_url, next_track_id }
        │
        ├──→ Browser pre-fetches next_url (no playback yet)
        │
        └──→ On current track end → Seamlessly play next_url

   Constraints:
   - No offline caching
   - No file saving/modification
   - Client handles pre-fetch logic

3. PLAYLIST FLOW (Authenticated)
────────────────────────────────
   User: Create playlist / Add tracks
        │
        ▼
   API: Validate session
        │
        ▼
   Storage: Save to JSON file
            playlists/{user_id}/{playlist_id}.json
        │
        ▼
   Frontend: Confirm save / Update UI

4. SHARING FLOW
──────────────
   User: Click "Share" on playlist
        │
        ▼
   API: Generate share token
        │
        ▼
   Storage: Save public link metadata
        │
        ▼
   Frontend: Display shareable URL
            /share/{share_token}

   Shared User: Visit share URL
                │
                ▼
   API: Load playlist from file
        │
                ▼
   Frontend: Display playlist (song names in order)
```

### 4.4 Technology Stack Recommendations

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Server** | Go (Golang) | Excellent concurrency for 1000+ users, small binary, fast startup |
| **Web Server** | Chi (Go router) or Express (Node) | Lightweight, battle-tested |
| **YouTube Integration** | yt-dlp + go-yt-dlp | Reliable extraction, active maintenance |
| **Storage** | File system (JSON) + Go generic cache | Simple, no database required |
| **Frontend** | Vanilla JS + Tailwind CSS | No build complexity, small bundle |
| **Player** | HTML5 Audio + YouTube IFrame API | Handles HLS/DASH automatically |
| **Sessions** | In-memory (Go map) + JWT tokens | Stateless, scalable horizontally if needed |
| **Deployment** | Docker + Docker Compose | Simple self-hosted deployment |

### 4.5 API Endpoints Design

```
AUTHENTICATION
──────────────
POST   /api/auth/register       # Create new account
POST   /api/auth/login          # Login, returns session token
POST   /api/auth/logout         # Invalidate session
GET    /api/auth/me             # Current user info

SEARCH
──────
GET    /api/search?q={query}              # Search YouTube tracks
GET    /api/search/playlists?q={query}   # Search public playlists
GET    /api/search/podcasts               # Podcast-focused search
GET    /api/search/music                  # Music-focused search
GET    /api/discover/playlists            # Browse public playlists (no query)

TRACKS
──────
GET    /api/tracks/{id}/stream    # Get stream URL (resolves just-in-time)
GET    /api/tracks/{id}/info      # Get track metadata
GET    /api/tracks/{id}/related   # Get related videos from yt-dlp
POST   /api/tracks/{id}/next     # Pre-fetch next track URL (gapless)

PLAYLISTS (Authenticated)
─────────────────────────
GET    /api/playlists           # List user's playlists
POST   /api/playlists           # Create new playlist
GET    /api/playlists/{id}      # Get playlist details
PUT    /api/playlists/{id}      # Update playlist
DELETE /api/playlists/{id}      # Delete playlist

PLAYLIST TRACKS
───────────────
POST   /api/playlists/{id}/tracks     # Add track to playlist
DELETE /api/playlists/{id}/tracks     # Remove track from playlist
PUT    /api/playlists/{id}/tracks     # Reorder tracks

SHARING
───────
POST   /api/playlists/{id}/share      # Generate share link
GET    /api/share/{token}             # Access shared playlist (public)

USERS
─────
GET    /api/users/{id}/playlists      # Get user's public playlists
```

### 4.6 JSON Data Model

```json
// playlists/{user_id}/{playlist_id}.json
{
  "id": "pl_abc123def456",
  "name": "Morning Commute",
  "description": "Upbeat tracks for the drive to work",
  "user_id": "user_xyz789",
  "is_public": false,
  "share_token": null,
  "tracks": [
    {
      "id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up",
      "duration": 213,
      "added_at": "2026-02-06T10:30:00Z",
      "position": 0
    },
    {
      "id": "another_video_id",
      "title": "Another Track Title",
      "duration": 180,
      "added_at": "2026-02-06T10:35:00Z",
      "position": 1
    }
  ],
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:35:00Z"
}

// users/{user_id}/user.json
{
  "id": "user_xyz789",
  "username": "musiclover",
  "email": "user@example.com",
  "password_hash": "bcrypt_hash_here",
  "created_at": "2026-01-01T00:00:00Z",
  "preferences": {
    "default_volume": 0.7,
    "auto_play": true,
    "repeat_mode": "none",  // "none" | "track" | "playlist"
    "theme": "dark"
  }
}

// sessions/{session_id}.json (ephemeral)
{
  "user_id": "user_xyz789",
  "expires_at": "2026-02-07T00:00:00Z",
  "created_at": "2026-02-06T00:00:00Z"
}

// share_tokens/{share_token}.json
{
  "token": "share_abc123",
  "playlist_id": "pl_abc123def456",
  "created_at": "2026-02-06T10:00:00Z",
  "expires_at": null,
  "view_count": 0
}
```

---

## 5. User Flow Walkthrough

### 5.1 Anonymous User Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                     ANONYMOUS USER EXPERIENCE                        │
└──────────────────────────────────────────────────────────────────────┘

1. LANDING
   ───────
   User opens browser → https://music.local
   │
   ├─→ Homepage loads (static HTML)
   │
   ├─→ User sees:
   │   • Search bar (prominent)
   │   • Featured playlists (if any)
   │   • "Login to create playlists" CTA
   │
   └─→ [Option A] Search for content

2. SEARCH & PLAY (Anonymous)
   ──────────────────────────
   User types "lofi hip hop radio" → Press Enter
   │
   ├─→ API call: GET /api/search?q=lofi+hip+hop
   │
   ├─→ yt-dlp searches YouTube
   │
   ├─→ Returns: [{id, title, duration, thumbnail}, ...]
   │
   ├─→ Frontend displays results grid
   │
   └─→ User clicks "▶ Play" on track #3
       │
       ├─→ API: GET /api/tracks/{id}/stream
       │
       ├─→ yt-dlp resolves stream URL (just-in-time)
       │
       ├─→ Frontend embeds YouTube player with stream URL
       │
       └─→ Audio begins playing

3. BROWSE SHARED PLAYLIST
   ───────────────────────
   Friend shares link: https://music.local/share/abc123
   │
   ├─→ User visits link
   │
   ├─→ API loads playlist by share token
   │
   ├─→ Returns: Playlist with track list (names only)
   │
   ├─→ Frontend displays: "Chill Vibes - 12 tracks"
   │
   ├─→ User sees table: Track # | Title | Duration
   │
   └─→ User can play any track (same as #2)
```

### 5.2 Authenticated User Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                   AUTHENTICATED USER EXPERIENCE                       │
└──────────────────────────────────────────────────────────────────────┘

1. AUTHENTICATION
   ───────────────
   User clicks "Login" → Shows login form
   │
   ├─→ Enters credentials → POST /api/auth/login
   │
   ├─→ Server validates → Returns session token (JWT)
   │
   ├─→ Frontend stores token in localStorage
   │
   └─→ UI updates: Shows username, "Create Playlist" button

2. CREATE PLAYLIST
   ───────────────
   User clicks "Create Playlist"
   │
   ├─→ Modal: "Name your playlist" → "Road Trip 2026"
   │
   ├─→ POST /api/playlists {name: "Road Trip 2026"}
   │
   ├─→ Server creates file: playlists/user_x/road-trip-2026.json
   │
   ├─→ Frontend redirects to playlist page
   │
   └─→ Empty playlist displayed with "Add tracks" CTA

3. BUILD PLAYLIST
   ──────────────
   User searches: "road trip songs 2024"
   │
   ├─→ Search results appear
   │
   └─→ User clicks "+" on 5 tracks
       │
       ├─→ POST /api/playlists/{id}/tracks {track_id: "abc"}
       │
       ├─→ Server updates JSON file
       │
       └─→ Frontend updates playlist UI

4. PLAY & ENJOY
   ─────────────
   User clicks "▶ Play All" on playlist
   │
   ├─→ Frontend initiates first track stream
   │
   ├─→ On completion → Auto-play next track
   │
   └─→ Queue UI shows upcoming tracks

5. SHARE PLAYLIST
   ───────────────
   User clicks "Share" button
   │
   ├─→ Modal: "Copy share link" → https://music.local/share/xyz789
   │
   ├─→ POST /api/playlists/{id}/share
   │
   ├─→ Server generates share token → Saves to file
   │
   └─→ User copies link → Sends to friend
```

---

## 6. Key Assumptions to Verify

### 6.1 Technical Assumptions

| # | Assumption | Verification Method |
|---|------------|---------------------|
| A1 | yt-dlp can handle 1000 concurrent extractions | Load test with simulated users |
| A2 | YouTube doesn't rate-limit stream requests | Monitor 429 responses during peak |
| A3 | JSON file I/O is fast enough for playlist ops | Benchmark file read/write latency |
| A4 | In-memory sessions scale to 1000 users | Memory profiling under load |
| A5 | yt-dlp format selection favors HLS/DASH | Test extraction output formats |

### 6.2 User Behavior Assumptions

| # | Assumption | Risk Level |
|---|------------|------------|
| U1 | Most users browse, few create playlists | Medium |
| U2 | Search is the primary discovery method | Low |
| U3 | Playlist sharing is occasional, not constant | Low |
| U4 | Stream-on-demand model (no pre-loading) | Low |

### 6.3 Infrastructure Assumptions

| # | Assumption | Verification |
|---|------------|--------------|
| I1 | Single server can handle 1000 concurrent users | Load test required |
| I2 | yt-dlp library remains functional | Monitor upstream changes |
| I3 | YouTube doesn't change API/embedding behavior | Periodic testing |

---

## 7. Potential Challenges and Solutions

### 7.1 YouTube Rate Limiting

| Challenge | Mitigation Strategy |
|-----------|---------------------|
| YouTube may throttle requests from single IP | Implement request queuing with exponential backoff |
| Stream extraction could be slow under load | Cache metadata (not URLs) with 5-minute TTL |
| YouTube embeds may be blocked in some regions | Provide direct stream URLs when possible |

### 7.2 Concurrency Management

| Challenge | Mitigation Strategy |
|-----------|---------------------|
| 1000 concurrent yt-dlp extractions | Limit concurrent extractions (e.g., 50 max queue) |
| Memory pressure from in-memory sessions | Use Go's built-in memory management + periodic cleanup |
| File I/O contention on playlist files | Implement file locking or per-user directories |

### 7.3 Streaming Performance

| Challenge | Mitigation Strategy |
|-----------|---------------------|
| Stream URL expiration during playback | yt-dlp extracts fresh URL per play request |
| Buffer delays for users on slow connections | Pre-buffer first 30 seconds (without caching) |
| YouTube format availability issues | Fallback to lower quality formats |

### 7.4 Storage Scalability

| Challenge | Mitigation Strategy |
|-----------|---------------------|
| Many small JSON files → filesystem overhead | Batch small files into larger ones after threshold |
| Search performance degrades with more playlists | Implement in-memory search index |
| Backup/restore complexity | Use tar + gzip for playlist directories |
| File size exceeds 2MB limit | Reject uploads with clear error message |

### 7.5 Security Considerations

| Challenge | Mitigation Strategy |
|-----------|---------------------|
| Malicious URLs in playlists | Validate all track IDs are YouTube IDs |
| Session hijacking | Use HTTP-only cookies, short session TTL |
| DoS attacks on search | Implement rate limiting (e.g., 10 req/min) |
| Share token enumeration | Use UUIDs (not sequential) for tokens |
| Large file uploads | Enforce 2MB limit on all file operations |

### 7.6 Playback Edge Cases

| Scenario | Behavior |
|----------|----------|
| Track removed during playback | Skip to next track (TEST-011) |
| Region blocked content | Show error message, auto-skip or user action (TEST-012) |
| Repeat track enabled | Loop current track infinitely |
| Repeat playlist enabled | Loop entire playlist from first track |
| Track unavailable (deleted) | Show error, remove from playlist |

---

## 8. Implementation Roadmap

### Phase 1: Core Foundation (Weeks 1-2)
- [ ] Set up Go project structure
- [ ] Implement yt-dlp wrapper
- [ ] Create basic HTTP server with routing
- [ ] Build static frontend (HTML/CSS/JS)
- [ ] Implement track search and streaming

### Phase 2: Authentication & Playlists (Weeks 3-4)
- [ ] User registration/login flows
- [ ] Playlist CRUD operations
- [ ] JSON file storage layer
- [ ] Session management
- [ ] Basic UI for playlist management

### Phase 3: Sharing & Polish (Weeks 5-6)
- [ ] Share link generation
- [ ] Public playlist viewing
- [ ] UI/UX improvements
- [ ] Mobile responsiveness
- [ ] Error handling and logging

### Phase 4: Performance & Scale (Weeks 7-8)
- [ ] Load testing (1000 concurrent users)
- [ ] Optimize yt-dlp extraction
- [ ] Implement caching layer
- [ ] Rate limiting
- [ ] Monitoring and alerting

---

## 9. File Structure

```
music-streaming-service/
├── cmd/
│   └── server/
│       └── main.go              # Entry point
├── internal/
│   ├── api/
│   │   ├── handlers/            # HTTP handlers
│   │   ├── middleware/          # Auth, logging, rate limit
│   │   └── routes/              # Route definitions
│   ├── auth/
│   │   └── service.go          # Authentication logic
│   ├── playlist/
│   │   ├── service.go          # Playlist business logic
│   │   └── storage.go          # JSON file operations
│   ├── search/
│   │   └── service.go          # YouTube search via yt-dlp
│   ├── streaming/
│   │   └── service.go          # Stream URL resolution
│   └── storage/
│       └── manager.go          # File system abstraction
├── pkg/
│   ├── yt-dlp/
│   │   └── client.go            # yt-dlp bindings (bundled binary)
│   └── models/
│       └── types.go            # Data models
├── yt-dlp/                       # Bundled yt-dlp binary
│   ├── yt-dlp                   # Pre-built binary
│   └── yt-dlp.conf              # Configuration
├── storage/
│   ├── playlists/              # Playlist JSON files
│   │   └── {user_id}/
│   │       └── {playlist_id}.json
│   ├── users/                  # User JSON files
│   │   └── {user_id}.json
│   └── sessions/              # Session files (optional)
├── web/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   ├── player.js
│   │   │   └── api.js
│   │   └── images/
│   └── templates/
│       ├── index.html
│       ├── playlist.html
│       └── login.html
├── config/
│   └── config.yaml             # Configuration file
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first audio | <2s | From play click to audio start |
| Playlist save latency | <100ms | POST /api/playlists response |
| Search response time | <500ms | GET /api/search response |
| Concurrent stream capacity | 1000 | Load test verification |
| Uptime | 99.5% | Monthly monitoring |
| Storage efficiency | <10GB | Per 1000 playlists |

---

## 11. Conclusion

This architecture provides a simple, self-hosted music and podcast streaming service that meets all specified requirements while maintaining scalability and performance. The key innovations are:

1. **Just-in-time URL resolution** prevents caching issues and respects YouTube's expiration mechanisms
2. **File-based storage** eliminates database complexity while maintaining data durability
3. **Monolithic design** simplifies deployment and reduces operational overhead
4. **YouTube as source** provides vast content library without licensing concerns

The modular design allows individual components to be optimized or replaced as needs evolve, while the conservative technical choices ensure reliability and ease of maintenance.

---

## 12. Additional Requirements Summary (v2.0)

### 12.1 Playback Features
- **Gapless Playback:** T-15s pre-fetch, browser handles pre-fetch logic
- **Repeat Modes:** Track repeat, Playlist repeat, None
- **Persistent Volume:** Per-user volume preference saved in user profile

### 12.2 Discovery Features
- **Related Videos:** Fetched via yt-dlp related videos endpoint
- **Playlist Search:** Search public playlists separately from main search
- **Public Playlist Discovery:** Dedicated page for browsing discoverable playlists

### 12.3 Sharing Features
- **Android Native Share:** Web Share API integration for Android devices
- **Platform-Wide:** Share available on all content types

### 12.4 Constraints (Reaffirmed)
- **No Offline Mode:** Always requires network connection
- **No File Modification:** Streaming files cannot be changed or saved
- **yt-dlp Bundled:** Binary included in project directory
- **Playlist Metadata Cache:** 1-day TTL for cached metadata
- **File Size Limit:** 2MB max for all file operations

### 12.5 Error Handling
- **Track Removed:** Auto-skip to next track
- **Region Blocked:** Display error message to user

---

*Document updated with new requirements. Planning phase continues.*

---

## 13. MVP Requirements (v3.0 - Python + FastAPI)

### 13.1 MVP Scope

**What we're building:**
- Search field → finds YouTube videos
- Returns: `id`, `title`, `duration`, `audio_url` (direct CDN), `related_videos[]`
- Client streams audio directly (HTML5 Audio element)
- Server only: metadata + URL resolution (no audio proxying)

### 13.2 Technology Stack

```yaml
Server: Python 3.11 + FastAPI + Uvicorn
YouTube: yt-dlp (Python API)
Client: Vanilla JS + HTML5 Audio
Deployment: Docker
```

### 13.3 yt-dlp Python Implementation

```python
from fastapi import FastAPI, HTTPException
from yt_dlp import YoutubeDL
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class ResolveRequest(BaseModel):
    url: str

class TrackInfo(BaseModel):
    id: str
    title: str
    duration: int
    audio_url: str
    related: List[dict]

@app.post("/resolve", response_model=TrackInfo)
async def resolve_track(request: ResolveRequest):
    """Extract track metadata and audio URL (no download)."""
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'extract_flat': False,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            return {
                'id': info['id'],
                'title': info['title'],
                'duration': info.get('duration', 0),
                'audio_url': info['url'],
                'related': [
                    {'id': v['id'], 'title': v['title'], 'duration': v.get('duration')}
                    for v in info.get('related_videos', [])[:10]
                ] if info.get('related_videos') else []
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 13.4 Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    yt-dlp

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 13.5 Constraints (MVP)

- `related_videos` is **best-effort** (may be empty, order may differ from YouTube UI)
- Audio-only: `audio_url` is direct CDN stream, not YouTube iframe
- Server only resolves metadata + stream URL (no audio proxying)
- No playlist persistence in MVP
- No authentication in MVP

---

## 14. UI Requirements (v3.0)

### 14.1 Five Primary UI Regions

```
┌────────────────────────────────────────────────────────────┐
│  [☰]  Music    [ 🔍 Search input...           ]  [👤]   │  ← Top Navigation Bar
├────────────┬───────────────────────────────────┬─────────┤
│            │                                   │         │
│  Sidebar   │         Main Content              │  Right  │  ← Left Sidebar
│            │         Area                       │  Panel  │
│  - Home    │                                   │         │
│  - Explore │    ┌─────────────────────┐        │  ────   │
│  - Library │    │  🎵 Album Artwork   │        │  Related│  ← Right Panel
│            │    │  Track Title         │        │  Videos │  (MVP: Related only)
│            │    │  Artist Name         │        │  (List) │
│            │    └─────────────────────┘        │         │
│            │                                   │         │
├────────────┴───────────────────────────────────┴─────────┤
│  [🎵] [Thumbnail] Title - Artist    [⏮] [▶/⏸] [⏭]       │  ← Bottom Player Bar
│                      [━━━●━━━━━━━] 0:45 / 3:33   [🔊]      │
└────────────────────────────────────────────────────────────┘
```

### 14.2 Top Navigation Bar (Header)

**Elements:**
- Left: Hamburger menu icon + App identity ("Music")
- Center: Search input field
- Right: User avatar / profile access

**Behavior:**
- Always visible
- Search is global and context-independent

### 14.3 Left Sidebar (Minimal MVP)

**Sections:**
- Home
- Explore
- Library

**Behavior:**
- Persistent navigation only
- No playback control

### 14.4 Main Content Area

**MVP Elements:**
- Large square album artwork
- Track title overlay
- Artist name overlay

**Behavior:**
- Displays currently playing track
- Search results appear here (not in right panel)
- Artwork is passive context, not navigation

### 14.5 Right Panel (Contextual Queue - MVP)

**MVP Only:**
- Tab: Related (skip Lyrics/Up Next)
- Related videos list: Each row contains:
  - Track title
  - Artist
  - Duration (right-aligned)
- Behavior: Click = immediate playback

### 14.6 Bottom Player Bar (MVP)

**Elements:**
- Left: Previous / Play / Pause / Next
- Center: Timeline / Progress Bar (current time vs total)
- Track Info: Thumbnail + Title + Artist
- Right: Volume

**Behavior:**
- Always visible
- Playback survives navigation
- HTML5 `<audio>` element abstraction

### 14.7 MVP Data Flow

```
1. User searches → Top Bar
2. Results → Display in main content area
3. Click result → Bottom player starts playing (audio only)
4. Related videos → Right panel populates
5. Click related → Updates player + right panel
```

---

## 16. Implementation Plan (Step-by-Step)

### Phase 1: Backend Foundation (Module: API Server)

#### 1.1 Project Setup
- [ ] Create `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `yt-dlp`, `python-multipart`
- [ ] Create `main.py` with FastAPI app initialization
- [ ] Create `config.py` for configuration management (optional for MVP)
- [ ] Setup project directory structure

#### 1.2 yt-dlp Integration Module
**File:** `yt_dlp_client.py`
**Responsibility:** Encapsulate all yt-dlp interactions

**Interfaces:**
```python
class YTDLPCClient:
    def resolve_track(url: str) -> TrackInfo:
        """Extract metadata + audio URL from YouTube URL."""
        
    def extract_video_id(url: str) -> str | None:
        """Parse YouTube URL to extract video ID."""
```

**Test Boundaries:**
- Unit test: Extract video ID from various URL formats
- Unit test: Handle invalid URLs gracefully
- Integration test: Resolve real YouTube URLs
- Integration test: Verify `audio_url` is not None for valid videos

#### 1.3 API Endpoints Module
**File:** `api/routes.py`
**Responsibility:** HTTP request handling

**Endpoints:**
```python
POST /resolve
  Input: { "url": str }
  Output: TrackInfo
  Status Codes: 200, 400 (invalid URL), 500 (extraction error)
```

**Test Boundaries:**
- Unit test: Request validation (missing url, invalid format)
- Integration test: Real API call returns expected structure
- Load test: 100 concurrent resolve requests

#### 1.4 Error Handling Module
**File:** `api/errors.py`
**Responsibility:** Centralized error responses

**Error Types:**
- `InvalidURLError` (400)
- `ExtractionError` (500)
- `RateLimitError` (429)

---

### Phase 2: Frontend Foundation (Module: UI Shell)

#### 2.1 HTML Structure
**File:** `web/index.html`
**Responsibility:** DOM skeleton for 5 regions

**Regions:**
```html
<header id="top-bar">...</header>
<nav id="sidebar">...</nav>
<main id="main-content">...</main>
<aside id="right-panel">...</aside>
<footer id="player-bar">...</footer>
```

#### 2.2 CSS Styling
**File:** `web/css/styles.css`
**Responsibility:** Layout + responsive design

**Layout Requirements:**
- Grid layout for 5-region structure
- Fixed header/sidebar/footer, scrollable main + right panel
- Mobile responsiveness (hide sidebar/right panel on small screens)

**Test Boundaries:**
- Visual regression: Verify layout on different screen sizes
- Accessibility: Keyboard navigation works

---

### Phase 3: API Client Module

#### 3.1 API Client
**File:** `web/js/api.js`
**Responsibility:** HTTP communication with backend

**Interfaces:**
```javascript
class APIClient {
  async resolve(url: string): Promise<TrackInfo>
  async search(query: string): Promise<SearchResults>
}
```

**Test Boundaries:**
- Unit test: Mock fetch responses
- Integration test: Real API calls

#### 3.2 Error Handling
- Network failure: Show toast notification
- API error: Display error message in main content

---

### Phase 4: Search Functionality

#### 4.1 Search Input Component
**Location:** Top Bar (header)

**Behavior:**
- Real-time search on Enter key
- Debounced input (300ms) for live search (optional)
- Clear button when query is not empty

#### 4.2 Search Results Display
**Location:** Main Content Area

**Component:** `SearchResultsList`
**Data:**
```typescript
interface SearchResult {
  id: string;
  title: string;
  duration: number;
  thumbnail_url: string;
}
```

**Behavior:**
- Render grid of result cards
- Each card: thumbnail, title, duration, play button
- Click play → trigger player with selected track

**Test Boundaries:**
- Unit test: Render results correctly
- Integration test: Click triggers player update

---

### Phase 5: Player Module

#### 5.1 HTML5 Audio Wrapper
**File:** `web/js/player.js`
**Responsibility:** Abstraction over `<audio>` element

**Interfaces:**
```javascript
class AudioPlayer {
  play(track: TrackInfo): void
  pause(): void
  resume(): void
  seek(time: number): void
  setVolume(volume: 0-1): void
  on(event: string, callback: function): void
}
```

**Events:**
- `loadedmetadata`: Duration known
- `timeupdate`: Progress update
- `ended`: Track finished
- `error`: Playback error

#### 5.2 Player Bar Integration
**Location:** Bottom Player Bar

**Controls:**
- Play/Pause toggle (icon swap)
- Previous/Next buttons
- Progress slider (range input)
- Volume slider (range input)
- Time display (current / total)

**Test Boundaries:**
- Unit test: Player state transitions
- Integration test: Audio plays from CDN URL
- Integration test: Progress updates during playback
- Integration test: Volume changes persist

---

### Phase 6: Related Videos Feature

#### 6.1 Related Videos Component
**Location:** Right Panel

**Component:** `RelatedVideosList`
**Data:**
```typescript
interface RelatedVideo {
  id: string;
  title: string;
  duration: number;
}
```

**Behavior:**
- Display list of related videos from `TrackInfo.related`
- Each item: title, duration
- Click → Update player with new track
- Update right panel with new related videos

**Test Boundaries:**
- Unit test: Render related videos list
- Integration test: Click updates player + related panel

---

### Phase 7: Docker & Deployment

#### 7.1 Docker Configuration
**File:** `Dockerfile`

```dockerfile
FROM python:3.11-slim

RUN pip install --no-cache-dirWORKDIR /app fastapi uvicorn[standard] yt-dlp
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 7.2 Docker Compose (Optional)
**File:** `docker-compose.yml`

```yaml
services:
  music-streaming:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./web:/app/web
```

---

### Module Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                        DEPENDENCY GRAPH                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────────────┐
│   frontend/   │         │     backend/         │
│   index.html  │         │     main.py          │
└──────┬───────┘         └──────────┬───────────┘
       │                           │
       ▼                           ▼
┌──────────────┐         ┌──────────────────────┐
│   css/       │         │  yt_dlp_client.py    │
│  styles.css  │         │  (yt-dlp wrapper)    │
└──────┬───────┘         └──────────┬───────────┘
       │                           │
       ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    web/js/ (DEPENDENCIES)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  api.js ──────▶ APIClient (HTTP calls to /resolve)         │
│     │                                                      │
│     ▼                                                      │
│  player.js ─────▶ AudioPlayer (HTML5 <audio> wrapper)       │
│     │                                                      │
│     ▼                                                      │
│  app.js ──────▶ Orchestrator (binds UI + API + Player)    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Test Boundaries Summary

| Module | Test Type | Coverage |
|--------|-----------|----------|
| yt_dlp_client | Unit | URL parsing, error handling |
| yt_dlp_client | Integration | Real YouTube resolution |
| api/routes | Unit | Request validation |
| api/routes | Integration | Full endpoint test |
| api/client | Unit | Mock responses |
| api/client | Integration | Real API calls |
| player | Unit | State transitions |
| player | Integration | Audio playback, CDN URL |
| search/results | Unit | Render logic |
| search/results | Integration | UI + API binding |
| related_videos | Unit | Render logic |
| related_videos | Integration | Click → Player update |

---

### Execution Order

1. **Phase 1** → Backend Foundation (yt-dlp + API)
2. **Phase 2** → Frontend Shell (HTML + CSS layout)
3. **Phase 3** → API Client (connect frontend to backend)
4. **Phase 4** → Search (input → results display)
5. **Phase 5** → Player (audio playback controls)
6. **Phase 6** → Related Videos (right panel functionality)
7. **Phase 7** → Docker + Deployment

**Total Phases:** 7
**MVP Definition:** Phases 1-6 complete, Phase 7 optional for deployment testing
