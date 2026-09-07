'use strict';
(async () => {
  const explorer = document.querySelector('#motion-explorer');
  const detail = document.querySelector('#motion-detail');
  const notes = {
    control: ['Original motion: retention passes', 'Both checkpoints complete and qualify every rollout. Global error rises 8.79%; local error decreases 0.97%. This repeats the original-motion comparison at a new evaluation seed, not a new training origin.'],
    arc: ['Curved walking: survival is not faithful tracking', 'Completion stays above 98%, but no rollout qualifies for either checkpoint. R1 global error increases 49.45%, failing relative retention. The origin is already outside the task-quality limits.'],
    sideways: ['Sideways walking: a relative improvement is insufficient', 'R1 reduces global error by 26.27%, but both checkpoints still score 0% tracking-qualified execution. Passing the relative budget does not establish an absolute task capability.'],
    stoop: ['Neutral stooping: neither checkpoint completes', 'Both policies have 0% completion and qualification. Errors are measured only over the observed part of each terminated episode; their relative comparison cannot establish a solved skill.']
  };
  try {
    const response = await fetch('data/recovery-progress-2026-09-07.json');
    if (!response.ok) throw new Error('Snapshot unavailable');
    const data = await response.json();
    function render(motion) {
      const pair = Object.fromEntries(data.motion_screen.cells.filter(c => c.motion === motion).map(c => [c.arm, c.summary]));
      const heading = document.createElement('h3'); heading.textContent = notes[motion][0];
      const stats = document.createElement('div'); stats.className = 'mini-stats';
      for (const arm of ['origin', 'R1']) {
        const stat = document.createElement('span');
        const number = document.createElement('strong'); number.textContent = `${(100 * pair[arm].tracking_success_rate).toFixed(0)}%`;
        stat.append(number, `${arm === 'origin' ? 'Origin' : 'R1'} tracking-qualified`); stats.append(stat);
      }
      const explanation = document.createElement('p'); explanation.textContent = notes[motion][1];
      detail.replaceChildren(heading, stats, explanation);
      explorer.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.motion === motion)));
    }
    explorer.querySelectorAll('button').forEach(b => b.addEventListener('click', () => render(b.dataset.motion)));
    render('control'); explorer.hidden = false;
  } catch (_) {
    // The full result table and interpretation remain available without JavaScript or fetch.
    explorer.hidden = true;
  }
})();
