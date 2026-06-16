# Frontend Development Guide

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- Git

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/Aykacius/BeatForge.git
cd BeatForge/frontend

# Install dependencies
npm install

# Copy environment template
cp .env.local.example .env.local

# Configure .env.local with your settings
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev

# Open http://localhost:3000
```

## Project Structure

### `src/app/`
Next.js App Router pages and layouts.

- **layout.tsx**: Root layout with global providers
- **page.tsx**: Home page with upload area
- **generation/[jobId]/page.tsx**: Generation progress page
- **results/[jobId]/page.tsx**: Results and download page

### `src/components/`
Reusable React components.

- **UploadArea.tsx**: Drag-and-drop file upload
- **SettingsForm.tsx**: Difficulty and mapping style selection
- **ProgressIndicator.tsx**: Real-time generation progress
- **ResultsDisplay.tsx**: Download and beatmap info display

### `src/hooks/`
Custom React hooks for business logic.

- **useGeneration.ts**: Manages generation request and state
- **useJobStatus.ts**: Polls job status and updates UI

### `src/lib/`
Utility functions and API client.

- **api.ts**: Axios instance and API endpoints
- **types.ts**: TypeScript type definitions

## Component Details

### UploadArea Component

```typescript
// src/components/UploadArea.tsx

export interface UploadAreaProps {
  onFileSelected: (file: File) => void;
  isLoading?: boolean;
  error?: string;
}

export default function UploadArea({
  onFileSelected,
  isLoading,
  error,
}: UploadAreaProps) {
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files?.length > 0) {
      validateAndUpload(files[0]);
    }
  };

  const validateAndUpload = (file: File) => {
    const validFormats = ['audio/mpeg', 'audio/wav', 'audio/ogg'];
    const maxSize = 50 * 1024 * 1024; // 50MB

    if (!validFormats.includes(file.type)) {
      // Show error
      return;
    }

    if (file.size > maxSize) {
      // Show error
      return;
    }

    onFileSelected(file);
  };

  return (
    <div
      className={`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg ${
        isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {/* Component content */}
    </div>
  );
}
```

### SettingsForm Component

```typescript
// src/components/SettingsForm.tsx

export interface GenerationSettings {
  difficulty: 'EASY' | 'NORMAL' | 'HARD' | 'INSANE' | 'EXPERT_PLUS';
  mappingStyle: 'TECHNICAL_STREAM' | 'JUMP' | 'HYBRID' | 'AIM' | 'STREAM_PRACTICE';
  targetStarRating: number;
}

export interface SettingsFormProps {
  onSubmit: (settings: GenerationSettings) => void;
  isLoading?: boolean;
}

export default function SettingsForm({ onSubmit, isLoading }: SettingsFormProps) {
  const [settings, setSettings] = useState<GenerationSettings>({
    difficulty: 'NORMAL',
    mappingStyle: 'HYBRID',
    targetStarRating: 4.5,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(settings);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Difficulty selection */}
      <fieldset>
        <legend className="text-lg font-semibold mb-3">Difficulty</legend>
        <div className="grid grid-cols-5 gap-2">
          {['EASY', 'NORMAL', 'HARD', 'INSANE', 'EXPERT_PLUS'].map((diff) => (
            <label key={diff} className="flex items-center">
              <input
                type="radio"
                name="difficulty"
                value={diff}
                checked={settings.difficulty === diff}
                onChange={(e) =>
                  setSettings({ ...settings, difficulty: e.target.value as any })
                }
                className="mr-2"
              />
              <span className="text-sm">{diff.replace('_', ' ')}</span>
            </label>
          ))}
        </div>
      </fieldset>

      {/* Mapping style selection */}
      <fieldset>
        <legend className="text-lg font-semibold mb-3">Mapping Style</legend>
        <div className="grid grid-cols-5 gap-2">
          {/* Similar radio button group */}
        </div>
      </fieldset>

      {/* Target star rating slider */}
      <div>
        <label className="block text-lg font-semibold mb-3">
          Target Star Rating: {settings.targetStarRating.toFixed(1)}★
        </label>
        <input
          type="range"
          min="2"
          max="9"
          step="0.1"
          value={settings.targetStarRating}
          onChange={(e) =>
            setSettings({
              ...settings,
              targetStarRating: parseFloat(e.target.value),
            })
          }
          className="w-full"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 bg-blue-500 text-white rounded-lg font-semibold disabled:bg-gray-400"
      >
        {isLoading ? 'Generating...' : 'Generate Beatmap'}
      </button>
    </form>
  );
}
```

### ProgressIndicator Component

```typescript
// src/components/ProgressIndicator.tsx

export interface JobProgress {
  status: string;
  progress: number;
  currentStage: string;
  estimatedTimeRemaining?: number;
}

export interface ProgressIndicatorProps {
  progress: JobProgress;
}

const STAGES = [
  'Validating file...',
  'Analyzing BPM...',
  'Detecting beats...',
  'Analyzing features...',
  'Detecting sections...',
  'Generating patterns...',
  'Packaging beatmap...',
  'Done!',
];

export default function ProgressIndicator({ progress }: ProgressIndicatorProps) {
  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress.progress}%` }}
        />
      </div>

      {/* Current stage */}
      <div className="text-center">
        <p className="text-lg font-semibold">{progress.currentStage}</p>
        <p className="text-gray-600">{progress.progress}% complete</p>
      </div>

      {/* Stage checklist */}
      <div className="space-y-2">
        {STAGES.map((stage, index) => {
          const isCompleted = index < STAGES.indexOf(progress.currentStage);
          const isCurrent = stage === progress.currentStage;

          return (
            <div key={stage} className="flex items-center space-x-2">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-white ${
                  isCompleted
                    ? 'bg-green-500'
                    : isCurrent
                    ? 'bg-blue-500 animate-pulse'
                    : 'bg-gray-300'
                }`}
              >
                {isCompleted && '✓'}
              </div>
              <span className={isCurrent ? 'font-semibold' : ''}>{stage}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

## Hooks

### useGeneration Hook

```typescript
// src/hooks/useGeneration.ts

export interface UseGenerationReturn {
  isLoading: boolean;
  error: string | null;
  jobId: string | null;
  uploadAndGenerate: (file: File, settings: GenerationSettings) => Promise<void>;
}

export function useGeneration(): UseGenerationReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);

  const uploadAndGenerate = async (
    file: File,
    settings: GenerationSettings
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Upload file
      const uploadResponse = await api.post('/upload', {
        file,
      });
      const songId = uploadResponse.data.song_id;

      // Step 2: Start generation
      const genResponse = await api.post('/generate', {
        song_id: songId,
        difficulty: settings.difficulty,
        mapping_style: settings.mappingStyle,
        target_star_rating: settings.targetStarRating,
      });
      
      setJobId(genResponse.data.job_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    jobId,
    uploadAndGenerate,
  };
}
```

### useJobStatus Hook

```typescript
// src/hooks/useJobStatus.ts

export interface UseJobStatusReturn {
  job: any | null;
  isLoading: boolean;
  error: string | null;
}

export function useJobStatus(jobId: string | null): UseJobStatusReturn {
  const [job, setJob] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    setIsLoading(true);

    // Poll job status every 2 seconds
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/jobs/${jobId}`);
        setJob(response.data);

        // Stop polling when complete
        if (response.data.status === 'COMPLETED' || response.data.status === 'FAILED') {
          clearInterval(interval);
        }
      } catch (err) {
        setError(err.message);
      }
    }, 2000);

    setIsLoading(false);

    return () => clearInterval(interval);
  }, [jobId]);

  return { job, isLoading, error };
}
```

## API Client

```typescript
// src/lib/api.ts

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

## Styling

The project uses TailwindCSS for styling. Configuration is in `tailwind.config.ts`:

```typescript
// tailwind.config.ts

import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'beatforge-blue': '#1e40af',
        'beatforge-purple': '#7c3aed',
      },
      animation: {
        'pulse-custom': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};

export default config;
```

## Pages

### Home Page

```typescript
// src/app/page.tsx

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import UploadArea from '@/components/UploadArea';
import SettingsForm from '@/components/SettingsForm';
import { useGeneration } from '@/hooks/useGeneration';

export default function Home() {
  const router = useRouter();
  const { uploadAndGenerate, isLoading, error, jobId } = useGeneration();
  const [file, setFile] = useState<File | null>(null);

  const handleFileSelected = (selectedFile: File) => {
    setFile(selectedFile);
  };

  const handleSettingsSubmit = async (settings: any) => {
    if (file) {
      await uploadAndGenerate(file, settings);
    }
  };

  // Redirect to generation page when job starts
  useEffect(() => {
    if (jobId) {
      router.push(`/generation/${jobId}`);
    }
  }, [jobId, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold text-center mb-4">BeatForge</h1>
          <p className="text-center text-gray-600 mb-8">
            Automatically generate osu!standard beatmaps from MP3 files
          </p>

          <div className="bg-white rounded-lg shadow-lg p-8 space-y-8">
            {!file ? (
              <UploadArea onFileSelected={handleFileSelected} isLoading={isLoading} error={error} />
            ) : (
              <>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-green-800">
                    ✓ File selected: <strong>{file.name}</strong>
                  </p>
                </div>
                <SettingsForm onSubmit={handleSettingsSubmit} isLoading={isLoading} />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
```

## Testing

```bash
# Run tests
npm run test

# Run with watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## Building for Production

```bash
# Build
npm run build

# Start production server
npm start
```
