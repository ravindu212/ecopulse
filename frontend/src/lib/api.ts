const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const ACCESS_TOKEN_KEY = "ecopulse_access_token";

export type AuthenticatedUser = {
  id: string;
  name: string;
  email: string;
  xp: number;
  current_streak: number;
  longest_streak: number;
  last_action_date: string | null;
  created_at: string;
  updated_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  user: AuthenticatedUser;
};

export type LoginInput = {
  email: string;
  password: string;
};

export type RegistrationInput = LoginInput & {
  name: string;
};

export type ProgressSummary = {
  xp: number;
  current_streak: number;
  longest_streak: number;
  completed_actions: number;
  estimated_co2e_kg_avoided: number;
};

export type CategoryActivity = {
  category: "transport" | "energy" | "food" | "waste";
  completed_actions: number;
  estimated_co2e_kg_avoided: number;
};

export type AssessmentHistoryItem = {
  assessment_date: string;
  overall_score: number;
  transport_score: number;
  energy_score: number;
  food_score: number;
  waste_score: number;
};

export type ProgressRecentActivity = {
  title: string;
  category: string;
  completed_at: string;
  xp_awarded: number;
  estimated_co2e_kg_awarded: number;
};

export type ProgressData = {
  summary: ProgressSummary;
  category_activity: CategoryActivity[];
  assessment_history: AssessmentHistoryItem[];
  recent_activity: ProgressRecentActivity[];
};

export type ChallengeAction = {
  id: string;
  title: string;
  slug: string;
  category: string;
  difficulty: string;
  sort_order: number;
};

export type Challenge = {
  id: string;
  title: string;
  slug: string;
  description: string;
  active: boolean;
  required_actions: ChallengeAction[];
};

export type JoinedChallenge = {
  challenge_id: string;
  title: string;
  slug: string;
  status: "active" | "completed" | "abandoned";
  joined_at: string;
  completed_at: string | null;
  completed_required_actions: number;
  total_required_actions: number;
  progress_percent: number;
};

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

export function getAccessToken() {
  return typeof window === "undefined" ? null : sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string) {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, token);
  window.dispatchEvent(new Event("ecopulse-auth"));
}

export function clearAccessToken() {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  window.dispatchEvent(new Event("ecopulse-auth"));
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail ?? "EcoPulse could not complete that request.", response.status);
  }
  return response.json() as Promise<T>;
}

export function listChallenges() {
  return apiFetch<Challenge[]>("/challenges");
}

export function listMyChallenges() {
  return apiFetch<JoinedChallenge[]>("/challenges/me");
}

export function joinChallenge(challengeId: string) {
  return apiFetch<JoinedChallenge>(`/challenges/${challengeId}/join`, { method: "POST" });
}

export function login(input: LoginInput) {
  return apiFetch<AuthResponse>("/auth/login", { method: "POST", body: JSON.stringify(input) });
}

export function register(input: RegistrationInput) {
  return apiFetch<AuthResponse>("/auth/register", { method: "POST", body: JSON.stringify(input) });
}

export function getCurrentUser() {
  return apiFetch<AuthenticatedUser>("/auth/me");
}

export function getProgress() {
  return apiFetch<ProgressData>("/progress");
}
