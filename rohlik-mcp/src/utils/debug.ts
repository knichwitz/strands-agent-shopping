// Debug logging utility for MCP server
// Set DEBUG=true in environment to enable

const DEBUG = process.env.DEBUG === 'true' || process.env.DEBUG === '1';

export function debugLog(context: string, data: any) {
  if (!DEBUG) return;
  
  const timestamp = new Date().toISOString();
  console.error(`[DEBUG ${timestamp}] ${context}:`);
  console.error(JSON.stringify(data));
  console.error('---');
}

export function isDebugEnabled(): boolean {
  return DEBUG;
}
