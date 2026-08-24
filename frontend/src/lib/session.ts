export type SessionData = {
  accessToken: string;
  organizationId: string;
};


const SESSION_KEY = "aios.session";


export function saveSession(
  session: SessionData,
): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(
    SESSION_KEY,
    JSON.stringify(session),
  );
}


export function getSession():
  | SessionData
  | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw =
    window.localStorage.getItem(
      SESSION_KEY,
    );

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as SessionData;
  } catch {
    clearSession();
    return null;
  }
}


export function clearSession(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(
    SESSION_KEY,
  );
}
