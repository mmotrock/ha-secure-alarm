/**
 * Secure Alarm Badge Card
 * Custom Lovelace card for Secure Alarm System
 * 
 * Installation:
 * 1. Copy to /config/www/secure-alarm-card.js
 * 2. Add to Lovelace resources:
 *    url: /local/secure-alarm-card.js
 *    type: module
 */

class SecureAlarmCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._pin = '';
    this._showInterface = false;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity');
    }
    this.config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.entity = hass.states[this.config.entity];
    
    if (this.entity) {
      this.render();
    }
  }

  getCardSize() {
    return 3;
  }

  render() {
    if (!this.entity) return;

    const state = this.entity.state;
    const isArmed = !['disarmed', 'arming'].includes(state);

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        ha-card {
          padding: 0;
          overflow: hidden;
        }
        .card-content {
          padding: 16px;
        }
        .badge-container {
          position: relative;
          cursor: pointer;
          transition: transform 0.3s;
        }
        .badge-container:hover {
          transform: scale(1.05);
        }
        .glow-outer {
          position: absolute;
          inset: 0;
          border-radius: 9999px;
          filter: blur(40px);
          opacity: 0.2;
          animation: pulse 2s infinite;
        }
        .badge-main {
          position: relative;
          background: var(--card-background-color, #1e293b);
          border-radius: 24px;
          padding: 32px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        .badge-icon-container {
          position: relative;
          margin: 0 auto;
        }
        .badge-icon-glow {
          position: absolute;
          inset: 0;
          border-radius: 9999px;
          filter: blur(20px);
          opacity: 0.3;
        }
        .badge-icon {
          position: relative;
          width: 160px;
          height: 160px;
          margin: 0 auto;
          border-radius: 9999px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .badge-icon svg {
          width: 96px;
          height: 96px;
          color: white;
        }
        .status-text {
          text-align: center;
          margin-top: 24px;
        }
        .status-title {
          font-size: 30px;
          font-weight: bold;
          color: var(--primary-text-color);
          margin-bottom: 8px;
        }
        .status-subtitle {
          font-size: 18px;
          color: var(--secondary-text-color);
        }
        .status-changed-by {
          font-size: 14px;
          color: var(--disabled-text-color);
          margin-top: 8px;
        }
        .tap-indicator {
          margin-top: 24px;
          text-align: center;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-size: 14px;
          color: var(--disabled-text-color);
        }
        .pulse-dot {
          width: 8px;
          height: 8px;
          background: var(--disabled-text-color);
          border-radius: 9999px;
          animation: pulse 2s infinite;
        }
        .entry-points {
          margin-top: 24px;
        }
        .entry-points-title {
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--disabled-text-color);
          margin-bottom: 12px;
        }
        .entry-point {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 10px 16px;
          border-radius: 9999px;
          margin-bottom: 8px;
          cursor: pointer;
          transition: all 0.3s;
          border: 1px solid;
        }
        .entry-point:hover {
          opacity: 0.8;
        }
        .entry-point-left {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .entry-point-icon {
          width: 16px;
          height: 16px;
        }
        .entry-point-name {
          color: var(--primary-text-color);
          font-size: 14px;
          font-weight: 500;
        }
        .entry-point-time {
          color: var(--disabled-text-color);
          font-size: 12px;
          margin-top: 2px;
        }
        .entry-point-right {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .entry-point-battery {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
        }
        .entry-point-status {
          font-size: 12px;
          font-weight: 500;
        }
        .interface-overlay {
          background: var(--card-background-color, #1e293b);
          border-radius: 24px;
          overflow: hidden;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        .interface-header {
          padding: 24px;
          color: white;
          position: relative;
        }
        .close-btn {
          position: absolute;
          top: 16px;
          right: 16px;
          background: rgba(255, 255, 255, 0.2);
          border: none;
          border-radius: 8px;
          padding: 8px;
          cursor: pointer;
          color: white;
        }
        .close-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        .interface-body {
          padding: 24px;
        }
        .arm-buttons {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .arm-button {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 24px;
          border-radius: 16px;
          border: none;
          cursor: pointer;
          transition: all 0.15s;
          font-size: 16px;
          color: white;
        }
        .arm-button:hover {
          transform: scale(1.05);
        }
        .arm-button:active {
          transform: scale(0.95);
        }
        .pin-display {
          background: var(--secondary-background-color, #334155);
          border-radius: 16px;
          padding: 16px;
          margin-bottom: 24px;
          text-align: center;
        }
        .pin-label {
          font-size: 14px;
          color: var(--disabled-text-color);
          margin-bottom: 8px;
        }
        .pin-dots {
          font-size: 30px;
          letter-spacing: 8px;
          color: var(--primary-text-color);
          min-height: 40px;
        }
        .pin-counter {
          font-size: 12px;
          color: var(--disabled-text-color);
          margin-top: 8px;
        }
        .keypad {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-bottom: 16px;
        }
        .key {
          background: var(--secondary-background-color, #334155);
          border: none;
          border-radius: 16px;
          padding: 24px;
          font-size: 24px;
          font-weight: 600;
          color: var(--primary-text-color);
          cursor: pointer;
          transition: all 0.15s;
        }
        .key:hover {
          transform: scale(1.05);
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .key:active {
          transform: scale(0.95);
        }
        .key.clear {
          background: #dc2626;
          color: white;
        }
        .key.enter {
          background: #16a34a;
          color: white;
        }
        .key.enter:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .green { background: #10b981; color: white; }
        .blue { background: #3b82f6; color: white; }
        .red { background: #ef4444; color: white; }
        .yellow { background: #eab308; color: white; }
        .orange { background: #f97316; color: white; }
        .green-border { border-color: rgba(16, 185, 129, 0.5); background: rgba(16, 185, 129, 0.2); }
        .red-border { border-color: rgba(239, 68, 68, 0.5); background: rgba(239, 68, 68, 0.2); }
        .green-text { color: #10b981; }
        .red-text { color: #ef4444; }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      </style>
      ${this._showInterface ? this.renderInterface() : this.renderBadge()}
    `;

    this.attachEventListeners();
  }

  renderBadge() {
    const state = this.entity.state;
    const changedBy = this.entity.attributes.changed_by || '';
    const { color, icon, text, description } = this.getStateInfo(state);
    const entryPoints = this.config.entry_points || [];

    return `
      <ha-card>
        <div class="card-content">
          <div class="badge-container" data-action="badge-click">
            <div class="glow-outer ${color}"></div>
            <div class="badge-main">
              <div class="badge-icon-container">
                <div class="badge-icon-glow ${color}"></div>
                <div class="badge-icon ${color}">
                  ${icon}
                </div>
              </div>
              <div class="status-text">
                <div class="status-title">${text}</div>
                <div class="status-subtitle">${description}</div>
                ${changedBy ? `<div class="status-changed-by">by ${changedBy}</div>` : ''}
              </div>
              <div class="tap-indicator">
                <div class="pulse-dot"></div>
                <span>Tap to ${state === 'disarmed' ? 'arm' : 'disarm'}</span>
              </div>
            </div>
          </div>
          ${entryPoints.length > 0 ? this.renderEntryPoints(entryPoints) : ''}
        </div>
      </ha-card>
    `;
  }

  renderEntryPoints(entryPoints) {
    return `
      <div class="entry-points">
        <div class="entry-points-title">Entry Points</div>
        ${entryPoints.map(point => this.renderEntryPoint(point)).join('')}
      </div>
    `;
  }

  renderEntryPoint(point) {
    const entity = this._hass.states[point.entity_id];
    if (!entity) return '';

    const isSecure = ['locked', 'closed'].includes(entity.state);
    const battery = point.battery_entity ? this._hass.states[point.battery_entity]?.state : null;
    const lastChanged = new Date(entity.last_changed);
    const timeAgo = this.getTimeAgo(lastChanged);

    return `
      <div class="entry-point ${isSecure ? 'green-border' : 'red-border'}" data-action="toggle-entry" data-entity="${point.entity_id}">
        <div class="entry-point-left">
          <div class="entry-point-icon ${isSecure ? 'green-text' : 'red-text'}">
            ${this.getEntryPointIcon(point.type, entity.state)}
          </div>
          <div>
            <div class="entry-point-name">${point.name}</div>
            <div class="entry-point-time">${timeAgo}</div>
          </div>
        </div>
        <div class="entry-point-right">
          ${battery ? `<div class="entry-point-battery">${this.getBatteryIcon(battery)} ${battery}%</div>` : ''}
          <div class="entry-point-status ${isSecure ? 'green-text' : 'red-text'}">
            ${entity.state.charAt(0).toUpperCase() + entity.state.slice(1)}
          </div>
        </div>
      </div>
    `;
  }

  renderInterface() {
    const state = this.entity.state;
    const isArmed = !['disarmed', 'arming'].includes(state);
    const { color, icon, text, description } = this.getStateInfo(state);

    if (!isArmed) {
      return this.renderArmOptions(color, icon, text, description);
    } else {
      return this.renderKeypad(color, icon, text, description);
    }
  }

  renderArmOptions(color, icon, text, description) {
    return `
      <ha-card>
        <div class="interface-overlay">
          <div class="interface-header ${color}">
            <button class="close-btn" data-action="close">
              <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
            <div style="display: flex; align-items: center; gap: 12px;">
              ${icon}
              <div>
                <div style="font-size: 20px; font-weight: bold;">${text}</div>
                <div style="font-size: 14px; opacity: 0.9;">${description}</div>
              </div>
            </div>
          </div>
          <div class="interface-body">
            <h3 style="color: var(--primary-text-color); margin-bottom: 16px;">Select Arm Mode</h3>
            <div class="arm-buttons">
              <button class="arm-button blue" data-action="arm-home">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                  </svg>
                  <div style="text-align: left;">
                    <div style="font-size: 20px;">Arm Home</div>
                    <div style="font-size: 14px; opacity: 0.8;">Perimeter only</div>
                  </div>
                </div>
                <div style="font-size: 30px;">→</div>
              </button>
              <button class="arm-button red" data-action="arm-away">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                  <div style="text-align: left;">
                    <div style="font-size: 20px;">Arm Away</div>
                    <div style="font-size: 14px; opacity: 0.8;">All zones + exit delay</div>
                  </div>
                </div>
                <div style="font-size: 30px;">→</div>
              </button>
            </div>
          </div>
        </div>
      </ha-card>
    `;
  }

  renderKeypad(color, icon, text, description) {
    const pinDots = '●'.repeat(this._pin.length) || '●●●●●●';
    return `
      <ha-card>
        <div class="interface-overlay">
          <div class="interface-header ${color}">
            <button class="close-btn" data-action="close">
              <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
            <div style="display: flex; align-items: center; gap: 12px;">
              ${icon}
              <div>
                <div style="font-size: 20px; font-weight: bold;">${text}</div>
                <div style="font-size: 14px; opacity: 0.9;">${description}</div>
              </div>
            </div>
          </div>
          <div class="interface-body">
            <div class="pin-display">
              <div class="pin-label">Enter PIN to Disarm</div>
              <div class="pin-dots">${pinDots}</div>
              <div class="pin-counter">${this._pin.length}/8 digits</div>
            </div>
            <div class="keypad">
              ${[1,2,3,4,5,6,7,8,9].map(n => `<button class="key" data-action="number" data-value="${n}">${n}</button>`).join('')}
              <button class="key clear" data-action="clear">✕</button>
              <button class="key" data-action="number" data-value="0">0</button>
              <button class="key enter" data-action="disarm" ${this._pin.length < 6 ? 'disabled' : ''}>✓</button>
            </div>
          </div>
        </div>
      </ha-card>
    `;
  }

  getStateInfo(state) {
    const states = {
      disarmed: { color: 'green', text: 'Disarmed', description: 'System Ready' },
      armed_home: { color: 'blue', text: 'Armed Home', description: 'Perimeter Secured' },
      armed_away: { color: 'red', text: 'Armed Away', description: 'Fully Armed' },
      arming: { color: 'yellow', text: 'Arming', description: 'Exit Delay' },
      pending: { color: 'orange', text: 'Entry Delay', description: 'Disarm Now' },
      triggered: { color: 'red', text: 'TRIGGERED!', description: 'Alarm Active' },
    };

    const info = states[state] || states.disarmed;
    info.icon = this.getIcon(state);
    return info;
  }

  getIcon(state) {
    const icons = {
      disarmed: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.618 5.984A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016zM12 9v2m0 4h.01"/></svg>',
      armed_home: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>',
      armed_away: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>',
      triggered: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
    };
    return icons[state] || icons.disarmed;
  }

  getEntryPointIcon(type, state) {
    if (type === 'door') {
      return state === 'locked' 
        ? '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>'
        : '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"/></svg>';
    } else {
      return state === 'closed'
        ? '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>'
        : '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/></svg>';
    }
  }

  getBatteryIcon(level) {
    const batteryLevel = parseInt(level);
    return `<svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7V3H8v4m8 0H8m8 0v10a2 2 0 01-2 2H10a2 2 0 01-2-2V7"/></svg>`;
  }

  getTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  }

  attachEventListeners() {
    this.shadowRoot.querySelectorAll('[data-action]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = el.dataset.action;
        
        switch(action) {
          case 'badge-click':
            this._showInterface = true;
            this.render();
            break;
          case 'close':
            this._showInterface = false;
            this._pin = '';
            this.render();
            break;
          case 'number':
            if (this._pin.length < 8) {
              this._pin += el.dataset.value;
              this.render();
            }
            break;
          case 'clear':
            this._pin = '';
            this.render();
            break;
          case 'arm-home':
            this.callService('secure_alarm', 'arm_home', { pin: '123456' });
            this._showInterface = false;
            this.render();
            break;
          case 'arm-away':
            this.callService('secure_alarm', 'arm_away', { pin: '123456' });
            this._showInterface = false;
            this.render();
            break;
          case 'disarm':
            if (this._pin.length >= 6) {
              this.callService('secure_alarm', 'disarm', { pin: this._pin });
              this._showInterface = false;
              this._pin = '';
              this.render();
            }
            break;
          case 'toggle-entry':
            const entityId = el.dataset.entity;
            const entity = this._hass.states[entityId];
            if (entity) {
              const domain = entityId.split('.')[0];
              const service = entity.state === 'locked' ? 'unlock' : 'lock';
              this.callService(domain, service, { entity_id: entityId });
            }
            break;
        }
      });
    });
  }

  callService(domain, service, data) {
    this._hass.callService(domain, service, data);
  }
}

customElements.define('secure-alarm-card', SecureAlarmCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'secure-alarm-card',
  name: 'Secure Alarm Badge Card',
  description: 'Badge-style alarm control with entry point management'
});