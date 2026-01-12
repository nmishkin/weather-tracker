import './style.css'

const trackBtn = document.querySelector('#track-btn');
const resultsContainer = document.querySelector('#results');
const loader = document.querySelector('#loader');

trackBtn.addEventListener('click', async () => {
  const threshold = parseInt(document.querySelector('#threshold').value);
  const consecutiveDays = parseInt(document.querySelector('#consecutive-days').value);
  const citiesInput = document.querySelector('#cities').value;
  const cities = citiesInput.split(',').map(c => c.trim()).filter(c => c.length > 0);

  if (isNaN(threshold) || isNaN(consecutiveDays) || cities.length === 0) {
    alert('Please enter a valid threshold, consecutive days, and at least one city.');
    return;
  }

  // Clear previous results
  resultsContainer.innerHTML = '';
  loader.style.display = 'block';

  try {
    const response = await fetch('./analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ threshold, cities, consecutive_days: consecutiveDays }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    renderResults(data.results, threshold, consecutiveDays);
  } catch (error) {
    console.error('Error fetching weather data:', error);
    resultsContainer.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: #f87171;">Error: Could not connect to the backend server. Make sure the FastAPI server is running.</p>`;
  } finally {
    loader.style.display = 'none';
  }
});

function renderResults(results, threshold, consecutiveDays) {
  if (results.length === 0) {
    resultsContainer.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: #94a3b8;">No data found for the specified cities.</p>`;
    return;
  }

  results.forEach(city => {
    const card = document.createElement('div');
    card.className = 'city-card';

    const badgeClass = city.meets_criteria ? 'met' : 'not-met';
    const badgeText = city.meets_criteria ? `🔥 ${consecutiveDays}+ Days Over ${threshold}°` : `Not ${consecutiveDays}+ days`;

    card.innerHTML = `
            <div class="city-header">
                <div>
                  <div class="city-name">${city.name}</div>
                  <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Florida, USA</div>
                </div>
                <div class="criteria-badge ${badgeClass}">
                    ${badgeText}
                </div>
            </div>
            <table class="forecast-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Day</th>
                        <th>High</th>
                        <th>Low</th>
                    </tr>
                </thead>
                <tbody>
                    ${city.forecast.map(day => `
                        <tr class="forecast-row ${day.is_match ? 'match' : ''}">
                            <td>${day.date}</td>
                            <td>${day.day}</td>
                            <td class="temp-high">${day.high !== null ? day.high + '°' : 'N/A'}</td>
                            <td class="temp-low">${day.low !== null ? day.low + '°' : 'N/A'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    resultsContainer.appendChild(card);
  });
}
