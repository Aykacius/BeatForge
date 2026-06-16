# BeatForge - Frontend Development

## Local Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Environment Setup

```bash
cp .env.example .env.local
# Edit .env.local with your settings
```

### Running Development Server

```bash
npm run dev
```

Open http://localhost:3000 in your browser.

### Building for Production

```bash
npm run build
npm start
```

### Type Checking

```bash
npm run type-check
```

## Project Structure

```
src/
├── app/              # Next.js app router
│   ├── layout.tsx
│   ├── page.tsx
│   ├── upload/
│   └── globals.css
├── components/       # React components
│   ├── FileUpload.tsx
│   ├── GenerationSettings.tsx
│   └── ProgressDisplay.tsx
├── lib/              # Utilities
│   ├── api.ts        # API client
│   └── store.ts      # Zustand store
└── public/           # Static assets
```

## Components

### FileUpload
Handles MP3 file upload with drag-and-drop support.

```tsx
<FileUpload onComplete={() => setStep('settings')} />
```

### GenerationSettings
Allows user to configure difficulty, style, and star rating.

```tsx
<GenerationSettings onComplete={() => setStep('progress')} />
```

### ProgressDisplay
Shows real-time generation progress.

```tsx
<ProgressDisplay />
```

## State Management

Using Zustand for simple state management:

```typescript
const { file, settings, setFile, setSettings } = useUploadStore()
```

## API Integration

All API calls go through `src/lib/api.ts`:

```typescript
await api.uploadFile(file)
await api.generateBeatmap(params)
await api.getJobStatus(jobId)
await api.downloadBeatmap(jobId)
```

## Styling

- Tailwind CSS for utility classes
- Custom global styles in `globals.css`
- Dark theme with gradient accents

## Pages

- `/` - Home page with getting started
- `/upload` - Main upload and generation interface
- `/404` - Not found page

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000/api/v1)

## Development Workflow

1. Start dev server: `npm run dev`
2. Edit components and see hot reload
3. Type check: `npm run type-check`
4. Build: `npm run build`

## UI/UX Features

- Dark theme optimized for late-night mapping
- Responsive design for mobile and desktop
- Real-time progress updates
- Smooth animations and transitions
- Drag-and-drop file upload
- Interactive difficulty selector
- Visual progress indicators

## Performance

- Next.js 14 with App Router
- Static generation where possible
- Image optimization
- Code splitting
- API request caching with Zustand

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
