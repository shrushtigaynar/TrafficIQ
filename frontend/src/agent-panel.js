// Agent Panel UI Logic

let agentState = null;
let agentCurrentActionId = null;

/**
 * Initialize the agent panel UI
 */
function initAgentPanel() {
  const agentBtn = document.getElementById('agentToggleBtn');
  const closeBtn = document.getElementById('agentCloseBtn');
  
  if (agentBtn) {
    agentBtn.addEventListener('click', () => toggleAgentPanel());
  }
  if (closeBtn) {
    closeBtn.addEventListener('click', () => toggleAgentPanel(false));
  }
}

/**
 * Toggle agent panel visibility
 */
function toggleAgentPanel(show) {
  const panel = document.getElementById('agentPanel');
  const btn = document.getElementById('agentToggleBtn');
  
  if (show === undefined) {
    show = !panel.classList.contains('open');
  }
  
  if (show) {
    panel.classList.add('open');
    btn.classList.add('active');
  } else {
    panel.classList.remove('open');
    btn.classList.remove('active');
  }
}

/**
 * Run agent analysis on current city
 */
async function runAgentAnalysis(cityName) {
  if (!cityName) {
    showToast('Please select a city first');
    return;
  }
  
  // Show agent panel
  toggleAgentPanel(true);
  
  // Show loading state
  showAgentLoading();
  clearAgentActivityLog();
  addAgentLogEntry('INIT', 'Starting autonomous traffic analysis...');
  
  try {
    addAgentLogEntry('API', 'Sending request to agent...');
    
    const response = await fetch(API + '/api/agent/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ city_name: cityName })
    });
    
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail?.error || 'Agent analysis failed');
    }
    
    const result = await response.json();
    agentState = result;
    
    // Display the result
    if (result.status === 'approval_required') {
      addAgentLogEntry('PLAN', `Agent recommends: ${result.recommended_action.action}`);
      displayAgentProposal(result);
    } else if (result.status === 'monitoring') {
      displayAgentMonitoring(result);
    } else {
      displayAgentResult(result);
    }
    
    // Display activity log
    displayAgentActivityLog(result.steps);
    
  } catch (e) {
    showToast('Agent analysis failed: ' + e.message);
    displayAgentError(e.message);
  }
}

/**
 * Display agent loading state
 */
function showAgentLoading() {
  const content = document.getElementById('agentContent');
  content.innerHTML = `
    <div class="agent-empty-state">
      <div class="agent-loading">
        <div>Analyzing traffic...</div>
        <div class="agent-loading-dots">
          <div class="agent-loading-dot"></div>
          <div class="agent-loading-dot"></div>
          <div class="agent-loading-dot"></div>
        </div>
      </div>
    </div>
  `;
}

/**
 * Display agent proposal (waiting for approval)
 */
function displayAgentProposal(result) {
  const content = document.getElementById('agentContent');
  agentCurrentActionId = result.action_id;
  
  const problem = result.problem || {};
  const rootCause = result.root_cause || {};
  const trend = result.trend || {};
  const action = result.recommended_action || {};
  
  // Format confidence percentage
  const confidence = Math.round((rootCause.confidence || 0) * 100);
  
  // Format evidence
  const evidenceHtml = (rootCause.evidence || [])
    .map(e => `<div style="font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem;">• ${e}</div>`)
    .join('');
  
  // Format predictions
  const predictionsHtml = (trend.predictions || [])
    .map(p => `
      <div class="prediction-item">
        <span class="prediction-time">${p.hour}</span>
        <span class="prediction-score">${p.score}/10 ${p.level}</span>
      </div>
    `)
    .join('');
  
  // Trend icon
  let trendIcon = '→';
  let trendClass = 'trend-stable';
  if (trend.direction === 'WORSENING') {
    trendIcon = '📈';
    trendClass = 'trend-worsening';
  } else if (trend.direction === 'IMPROVING') {
    trendIcon = '📉';
    trendClass = 'trend-improving';
  }
  
  content.innerHTML = `
    <div class="agent-section">
      <div class="agent-section-title">🚨 Problem Detected</div>
      <div class="agent-problem-card">
        <div class="agent-problem-location">${result.location}</div>
        <div class="agent-problem-score">
          <span>Congestion:</span>
          <span class="agent-score-badge">${problem.congestion_score || 0}/10</span>
        </div>
        <div class="agent-problem-score">
          <span>Level:</span>
          <span>${problem.congestion_level || 'UNKNOWN'}</span>
        </div>
        <div class="agent-problem-score">
          <span>Speed:</span>
          <span>${problem.speed || 0} km/h / ${problem.free_flow_speed || 0} km/h</span>
        </div>
      </div>
    </div>
    
    <div class="agent-section">
      <div class="agent-section-title">🔍 Root Cause Analysis</div>
      <div class="agent-cause-card">
        <div class="agent-cause-title">${rootCause.cause || 'Unknown cause'}</div>
        <div class="agent-confidence">
          <span>Confidence:</span>
          <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${confidence}%"></div>
          </div>
          <span>${confidence}%</span>
        </div>
        ${evidenceHtml}
      </div>
    </div>
    
    <div class="agent-section">
      <div class="agent-section-title">📊 Traffic Prediction</div>
      <div class="agent-info-box">
        <div class="agent-trend">
          <span class="trend-icon ${trendClass}">${trendIcon}</span>
          <span>Trend: <strong>${trend.direction || 'UNKNOWN'}</strong></span>
        </div>
      </div>
      <div class="agent-predictions">
        ${predictionsHtml}
      </div>
    </div>
    
    <div class="agent-section">
      <div class="agent-section-title">💡 Recommended Action</div>
      <div class="agent-action-card">
        <div class="agent-action-title">${action.action || 'UNKNOWN'}</div>
        <div class="agent-action-detail">
          <span class="agent-action-label">Description:</span>
          <span class="agent-action-value">${action.description || 'N/A'}</span>
        </div>
        <div class="agent-action-detail">
          <span class="agent-action-label">Expected Impact:</span>
          <span class="agent-action-value">${action.expected_impact || 'N/A'}</span>
        </div>
        <div class="agent-action-detail">
          <span class="agent-action-label">Risk Level:</span>
          <span class="agent-action-value">${action.risk || 'UNKNOWN'}</span>
        </div>
        <div class="agent-action-detail">
          <span class="agent-action-label">Time to Implement:</span>
          <span class="agent-action-value">${action.implementation_time || 'N/A'}</span>
        </div>
      </div>
    </div>
    
    <div class="agent-approval-section">
      <div class="agent-approval-title">🤝 Human Decision Required</div>
      <div class="agent-approval-buttons">
        <button class="agent-btn agent-btn-approve" onclick="approveAgentAction('${agentCurrentActionId}')">
          ✓ Approve
        </button>
        <button class="agent-btn agent-btn-reject" onclick="rejectAgentAction('${agentCurrentActionId}')">
          ✕ Reject
        </button>
      </div>
    </div>
  `;
}

/**
 * Display agent monitoring state
 */
function displayAgentMonitoring(result) {
  const content = document.getElementById('agentContent');
  content.innerHTML = `
    <div class="agent-empty-state">
      <div style="font-size: 3rem;">✓</div>
      <div class="agent-empty-text">${result.message}</div>
      <div class="agent-empty-hint">All areas operating normally. Agent continues monitoring...</div>
    </div>
  `;
}

/**
 * Display agent execution result
 */
function displayAgentResult(result) {
  const content = document.getElementById('agentContent');
  content.innerHTML = `
    <div class="agent-result-section">
      <div class="agent-result-title">✓ Action Executed Successfully</div>
      <div class="agent-result-metric">
        <span>Before:</span>
        <span class="agent-result-value">${result.result?.congestion_before || 'N/A'}/10</span>
      </div>
      <div class="agent-result-metric">
        <span>After:</span>
        <span class="agent-result-value">${result.result?.congestion_after || 'N/A'}/10</span>
      </div>
      <div class="agent-result-metric">
        <span>Improvement:</span>
        <span class="agent-result-value">${result.result?.improvement_percentage || 'N/A'}%</span>
      </div>
      <div style="margin-top: 0.6rem; padding-top: 0.6rem; border-top: 1px solid rgba(34,197,94,.3); font-size: 0.8rem; color: var(--muted);">
        ${result.result?.message || 'Action completed.'}
      </div>
    </div>
  `;
}

/**
 * Display agent error
 */
function displayAgentError(errorMessage) {
  const content = document.getElementById('agentContent');
  content.innerHTML = `
    <div class="agent-empty-state">
      <div style="font-size: 3rem;">⚠️</div>
      <div class="agent-empty-text">Analysis Failed</div>
      <div style="font-size: 0.75rem; color: #ef4444; margin-top: 0.5rem; word-break: break-word;">
        ${errorMessage}
      </div>
    </div>
  `;
}

/**
 * Display agent activity log
 */
function displayAgentActivityLog(steps) {
  const log = document.getElementById('agentActivityLog');
  if (!log) return;
  
  log.innerHTML = (steps || [])
    .map(step => {
      const time = new Date(step.time).toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      });
      return `
        <div class="agent-log-entry">
          <span class="agent-log-time">${time}</span>
          <span class="agent-log-phase">${step.phase.toUpperCase()}</span>
          <span>${step.description}</span>
        </div>
      `;
    })
    .join('');
}

/**
 * Add single entry to activity log
 */
function addAgentLogEntry(phase, description) {
  const log = document.getElementById('agentActivityLog');
  if (!log) return;
  
  const time = new Date().toLocaleTimeString('en-US', { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  });
  
  const entry = document.createElement('div');
  entry.className = 'agent-log-entry';
  entry.innerHTML = `
    <span class="agent-log-time">${time}</span>
    <span class="agent-log-phase">${phase}</span>
    <span>${description}</span>
  `;
  
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
}

/**
 * Clear activity log
 */
function clearAgentActivityLog() {
  const log = document.getElementById('agentActivityLog');
  if (log) log.innerHTML = '';
}

/**
 * Approve the proposed action
 */
async function approveAgentAction(actionId) {
  if (!actionId) {
    showToast('No action to approve');
    return;
  }
  
  addAgentLogEntry('APPROVAL', 'Human approved the action');
  
  // Disable buttons
  disableAgentButtons(true);
  
  try {
    addAgentLogEntry('EXEC', 'Executing simulated intervention...');
    
    const response = await fetch(API + '/api/actions/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        action_id: actionId,
        approved: true 
      })
    });
    
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail?.error || 'Action execution failed');
    }
    
    const result = await response.json();
    
    addAgentLogEntry('MONITOR', 'Monitoring results...');
    await new Promise(r => setTimeout(r, 2000)); // Simulate monitoring
    addAgentLogEntry('FEEDBACK', 'Analyzing feedback...');
    
    // Display result
    displayAgentExecutionResult(result);
    
  } catch (e) {
    showToast('Action execution failed: ' + e.message);
    addAgentLogEntry('ERROR', `Execution error: ${e.message}`);
    displayAgentError(e.message);
  } finally {
    disableAgentButtons(false);
  }
}

/**
 * Reject the proposed action
 */
async function rejectAgentAction(actionId) {
  if (!actionId) {
    showToast('No action to reject');
    return;
  }
  
  addAgentLogEntry('APPROVAL', 'Human rejected the action');
  disableAgentButtons(true);
  
  try {
    addAgentLogEntry('REPLAN', 'Agent re-planning alternative approaches...');
    
    const response = await fetch(API + '/api/actions/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        action_id: actionId,
        approved: false 
      })
    });
    
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail?.error || 'Rejection failed');
    }
    
    await new Promise(r => setTimeout(r, 1500));
    
    addAgentLogEntry('COMPLETE', 'Agent will monitor and re-evaluate');
    
    const content = document.getElementById('agentContent');
    content.innerHTML = `
      <div class="agent-empty-state">
        <div style="font-size: 2.5rem;">⏸️</div>
        <div class="agent-empty-text">Action Rejected</div>
        <div style="font-size: 0.8rem; color: var(--muted); margin-top: 0.5rem;">
          Agent noted the rejection and will continue monitoring for alternative approaches.
        </div>
      </div>
    `;
    
  } catch (e) {
    showToast('Error: ' + e.message);
  } finally {
    disableAgentButtons(false);
  }
}

/**
 * Display execution result
 */
function displayAgentExecutionResult(result) {
  const content = document.getElementById('agentContent');
  
  if (result.status === 'executed' && result.result) {
    const res = result.result;
    const improvement = parseFloat(res.improvement_percentage) || 0;
    
    content.innerHTML = `
      <div class="agent-section">
        <div class="agent-section-title">✓ Action Executed</div>
        <div class="agent-result-section">
          <div class="agent-result-title">Congestion Reduction</div>
          <div class="agent-result-metric">
            <span>Before:</span>
            <span class="agent-result-value">${res.congestion_before || 0}/10</span>
          </div>
          <div class="agent-result-metric">
            <span>After:</span>
            <span class="agent-result-value">${res.congestion_after || 0}/10</span>
          </div>
          <div class="agent-result-metric">
            <span>Improvement:</span>
            <span class="agent-result-value" style="color: #22c55e; font-size: 1rem;">
              ${improvement.toFixed(1)}%
            </span>
          </div>
        </div>
        <div style="margin-top: 0.8rem; padding: 0.6rem; background: rgba(34,197,94,.1); border-radius: 0.35rem; border: 1px solid rgba(34,197,94,.3);">
          <div style="font-size: 0.8rem; color: #22c55e; font-weight: 700;">✓ SUCCESSFUL</div>
          <div style="font-size: 0.75rem; color: var(--muted); margin-top: 0.3rem;">
            ${res.message || 'The simulated intervention showed positive results.'}
          </div>
        </div>
      </div>
    `;
  } else if (result.status === 'rejected') {
    content.innerHTML = `
      <div class="agent-empty-state">
        <div style="font-size: 2.5rem;">⏸️</div>
        <div class="agent-empty-text">Action Rejected</div>
        <div style="font-size: 0.8rem; color: var(--muted); margin-top: 0.5rem;">
          ${result.message || 'The proposed action was rejected.'}
        </div>
      </div>
    `;
  }
}

/**
 * Enable/disable approval buttons
 */
function disableAgentButtons(disabled) {
  const btns = document.querySelectorAll('.agent-btn');
  btns.forEach(btn => btn.disabled = disabled);
}

/**
 * Initialize agent panel when document is ready
 */
document.addEventListener('DOMContentLoaded', () => {
  initAgentPanel();
});
