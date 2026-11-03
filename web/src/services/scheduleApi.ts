// Fetches a CSV from the public folder at runtime, so data changes do not require a rebuild
export async function fetchScheduleCsv(fileName: string, signal?: AbortSignal): Promise<string> {
  const url = `${import.meta.env.BASE_URL}${fileName}`;
  const response = await fetch(url, { cache: "no-cache", signal });

  if (!response.ok) {
    throw new Error(`No se pudo cargar ${fileName} (código ${response.status}).`);
  }

  return response.text();
}