
"use client";

import { useEffect, useState } from "react";

interface Item {
  id: number;
  name?: string;
  Umur?: number;
  description?: string;
  price?: number;
}

export default function Home() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const API_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  // Mengambil data dari FastAPI
  async function getItems() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/items`, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      const data = await response.json();

      if (!Array.isArray(data)) {
        throw new Error("Format data API tidak sesuai.");
      }

      setItems(data);
    } catch (err) {
      console.error(err);
      setError("Gagal mengambil data. Periksa server FastAPI.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    getItems();
  }, []);

  // Format harga menjadi Rupiah
  function formatRupiah(price?: number) {
    if (price == null) return "-";

    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      maximumFractionDigits: 0,
    }).format(price);
  }

  return (
    <main>
     
      <h3>Total Data: {items.length}</h3>


      {loading ? (
        <p>Sedang mengambil data...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <table border={1} cellPadding={8} cellSpacing={0}>
          <thead>
            <tr>
              <th>No.</th>
              <th>ID</th>
              <th>Nama</th>
              <th>Umur</th>
              <th>Deskripsi</th>
              <th>Harga</th>
            </tr>
          </thead>

          <tbody>
            {items.length > 0 ? (
              items.map((item, index) => (
                <tr key={item.id}>
                  <td>{index + 1}</td>
                  <td>{item.id}</td>
                  <td>{item.name || "-"}</td>
                  <td>{item.Umur ?? "-"}</td>
                  <td>{item.description || "-"}</td>
                  <td>{formatRupiah(item.price)}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6}>Belum ada data.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </main>
  );
}
