import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [stations, setStations] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get("/api/weather_stations/")
      .then((response) => {
        setStations(response.data.results ?? response.data);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div className="App">
      <h1>Weather</h1>
      <p>Метеостанции из API</p>
      {loading && <p>Загрузка…</p>}
      {error && <p className="error">Ошибка: {error}</p>}
      {!loading && !error && (
        <ul>
          {stations.map((station) => (
            <li key={station.id}>
              {station.place?.name ?? `Станция #${station.id}`}
            </li>
          ))}
        </ul>
      )}
      {!loading && !error && stations.length === 0 && <p>Нет данных</p>}
    </div>
  );
}

export default App;
