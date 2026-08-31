const API_URL = 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.detail || 'Request failed')
  }
  return data
}

export async function apiSignup({ username, email, password }) {
  return request('/api/signup', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  })
}

export async function apiLogin({ username, password }) {
  return request('/api/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export async function apiCreateProject({ user_id, name, source_type, source_url }) {
  return request('/api/projects', {
    method: 'POST',
    body: JSON.stringify({ user_id, name, source_type, source_url }),
  })
}

export async function apiListProjects(user_id) {
  return request(`/api/projects?user_id=${user_id}`)
}

export async function apiUploadFiles(project_id, files) {
  return request(`/api/projects/${project_id}/files`, {
    method: 'POST',
    body: JSON.stringify({ files }),
  })
}

export async function apiGetFiles(project_id) {
  return request(`/api/projects/${project_id}/files`)
}

export async function apiGetFile(project_id, path) {
  return request(`/api/projects/${project_id}/file?path=${encodeURIComponent(path)}`)
}

export async function apiScaffold(project_id, user_id) {
  return request(`/api/projects/${project_id}/scaffold`, {
    method: 'POST',
    body: JSON.stringify({ user_id }),
  })
}

export async function apiGetScans(project_id) {
  return request(`/api/projects/${project_id}/scans`)
}

export async function apiNetworkStart(user_id, iface) {
  return request('/api/network/start', {
    method: 'POST',
    body: JSON.stringify({ user_id, interface: iface }),
  })
}

export async function apiNetworkStop(session_id) {
  return request(`/api/network/stop?session_id=${session_id}`, {
    method: 'POST',
  })
}

export async function apiNetworkSessions(user_id) {
  return request(`/api/network/sessions?user_id=${user_id}`)
}

export async function apiNetworkPackets(session_id, limit = 200) {
  return request(`/api/network/sessions/${session_id}/packets?limit=${limit}`)
}

export function networkReportUrl(session_id) {
  return `${API_URL}/api/network/sessions/${session_id}/report`
}

export async function apiChat(user_id, message) {
  return request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ user_id, message }),
  })
}

export async function apiChatHistory(user_id) {
  return request(`/api/chat/history?user_id=${user_id}`)
}

export async function apiPentestTools() {
  return request('/api/pentest/tools')
}

export async function apiMcpStatus(tool) {
  return request(`/api/pentest/mcp/status?tool=${tool}`)
}

export async function apiMcpConnect(tool) {
  return request(`/api/pentest/mcp/connect?tool=${tool}`, { method: 'POST' })
}

export async function apiRunTool(project_id, user_id, tool) {
  return request(`/api/projects/${project_id}/pentest/run`, {
    method: 'POST',
    body: JSON.stringify({ user_id, tool }),
  })
}

export async function apiRunToolUrl(user_id, tool, url) {
  return request('/api/pentest/run-url', {
    method: 'POST',
    body: JSON.stringify({ user_id, tool, url }),
  })
}

export async function apiPentestResults(project_id) {
  return request(`/api/projects/${project_id}/pentest/results`)
}

export async function apiReportData(user_id) {
  return request(`/api/report/data?user_id=${user_id}`)
}

export function reportPdfUrl(user_id) {
  return `${API_URL}/api/report/pdf?user_id=${user_id}`
}

export async function apiCodeScan(project_id, user_id) {
  return request(`/api/projects/${project_id}/code-security/scan`, {
    method: 'POST',
    body: JSON.stringify({ user_id }),
  })
}

export async function apiCodeFindings(project_id) {
  return request(`/api/projects/${project_id}/code-security/findings`)
}

export async function apiDashboardGraphs(user_id) {
  return request(`/api/dashboard/graphs?user_id=${user_id}`)
}

// ==========================================
// KAVACH CYBER REASONING SYSTEM (CRS) CLIENT
// ==========================================
export async function apiGetAgents() {
  return request('/api/crs/agents')
}

export async function apiRunAgentMesh(project_id, user_id, agent_id, query = '') {
  return request(`/api/projects/${project_id}/crs/agent-mesh/run`, {
    method: 'POST',
    body: JSON.stringify({ user_id, agent_id, query }),
  })
}

export async function apiGetAgentTasks(project_id) {
  return request(`/api/projects/${project_id}/crs/agent-mesh/tasks`)
}

export async function apiGetKnowledgeGraph(project_id) {
  return request(`/api/projects/${project_id}/crs/knowledge-graph`)
}

export async function apiRunCRSPipeline(project_id, user_id, finding_id = null, target_file = null) {
  return request(`/api/projects/${project_id}/crs/pipeline/run`, {
    method: 'POST',
    body: JSON.stringify({ user_id, finding_id, target_file }),
  })
}

export async function apiTriggerFuzzing(project_id, file_path, cwe_id = 'CWE-120', iterations = 2500) {
  return request(`/api/projects/${project_id}/crs/fuzzing/trigger`, {
    method: 'POST',
    body: JSON.stringify({ file_path, cwe_id, iterations }),
  })
}

export async function apiGetCRSRuns(project_id) {
  return request(`/api/projects/${project_id}/crs/runs`)
}

export async function apiGetRunPatches(run_id) {
  return request(`/api/crs/runs/${run_id}/patches`)
}

export async function apiGetCertificates(project_id) {
  return request(`/api/projects/${project_id}/crs/certificates`)
}

export async function apiGetSingleCertificate(certificate_id) {
  return request(`/api/crs/certificates/${certificate_id}`)
}