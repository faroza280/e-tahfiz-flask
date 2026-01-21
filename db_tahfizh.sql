-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 21 Jan 2026 pada 03.44
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_tahfizh`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `absensi`
--

CREATE TABLE `absensi` (
  `id` int(11) NOT NULL,
  `santri_id` int(11) NOT NULL,
  `ustadz_id` int(11) NOT NULL,
  `status` varchar(20) NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `tanggal` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `absensi`
--

INSERT INTO `absensi` (`id`, `santri_id`, `ustadz_id`, `status`, `keterangan`, `tanggal`) VALUES
(1, 2, 4, 'Hadir', '', '2025-12-20 11:01:09'),
(2, 3, 4, 'Sakit', '', '2025-12-20 11:01:39'),
(5, 3, 1, 'Sakit', 'demam panas', '2026-01-10 01:26:49'),
(6, 18, 1, 'Hadir', '', '2026-01-12 21:15:00'),
(7, 19, 1, 'Hadir', '', '2026-01-12 21:15:07'),
(8, 3, 1, 'Sakit', '', '2026-01-12 21:15:16'),
(9, 20, 1, 'Alpha', '', '2026-01-12 21:15:23');

-- --------------------------------------------------------

--
-- Struktur dari tabel `konfigurasi`
--

CREATE TABLE `konfigurasi` (
  `id` int(11) NOT NULL,
  `nama_tpq` varchar(100) DEFAULT NULL,
  `alamat_tpq` varchar(200) DEFAULT NULL,
  `target_bulanan` int(11) DEFAULT 150
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `konfigurasi`
--

INSERT INTO `konfigurasi` (`id`, `nama_tpq`, `alamat_tpq`, `target_bulanan`) VALUES
(1, 'TPQ Nurul ulum', 'Jl. Pulesari, Desa kilang,Kec.Montong gading', 200);

-- --------------------------------------------------------

--
-- Struktur dari tabel `santri`
--

CREATE TABLE `santri` (
  `id` int(11) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `kelas` varchar(50) DEFAULT NULL,
  `ustadz_id` int(11) NOT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Aktif'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `santri`
--

INSERT INTO `santri` (`id`, `nama`, `kelas`, `ustadz_id`, `foto`, `status`) VALUES
(2, 'Aisyah Humaira', 'Kelas V B', 1, '1768049855_aisayah.jpg', 'Aktif'),
(3, 'Umar Al-Faruq', 'Kelas VI A', 1, '1766128121_Ustad-Handy-Bonny.jpg', 'Aktif'),
(18, 'Azizah', 'Kelas VI A', 1, '1768049759_azizah.jpg', 'Aktif'),
(19, 'Sohibul rahman', 'Kelas VI A', 1, '1768223467_faroza_web.jpg', 'Aktif'),
(20, 'Rofiqul', 'Kelas V B', 1, '1768223547_minato.jpg', 'Aktif');

-- --------------------------------------------------------

--
-- Struktur dari tabel `setoran`
--

CREATE TABLE `setoran` (
  `id` int(11) NOT NULL,
  `santri_id` int(11) NOT NULL,
  `ustadz_id` int(11) NOT NULL,
  `surat` varchar(100) NOT NULL,
  `ayat_awal` int(11) NOT NULL,
  `ayat_akhir` int(11) NOT NULL,
  `kualitas` varchar(10) NOT NULL,
  `catatan` text DEFAULT NULL,
  `tanggal` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `setoran`
--

INSERT INTO `setoran` (`id`, `santri_id`, `ustadz_id`, `surat`, `ayat_awal`, `ayat_akhir`, `kualitas`, `catatan`, `tanggal`) VALUES
(1, 2, 2, 'An-Naba', 1, 15, 'A', 'Lancar', '2025-11-11 21:20:16'),
(2, 3, 1, 'At-Takwir', 1, 5, 'B', 'Perbaiki makhraj', '2025-11-11 21:20:16'),
(8, 3, 1, 'At-Takwir', 10, 15, 'A', '', '2025-12-04 18:23:05'),
(12, 3, 1, 'Al-Kahf', 1, 70, 'A', '', '2025-12-05 10:55:34'),
(16, 2, 1, 'An-Naba\'', 15, 40, 'A', '', '2025-12-05 17:23:07'),
(22, 3, 4, 'Al-Baqarah', 1, 200, 'A', '', '2025-12-07 18:29:38'),
(26, 3, 4, 'Al-Baqarah', 1, 100, 'A', 'Lebih giat anakku', '2025-12-19 14:23:18'),
(27, 2, 4, 'Al-Baqarah', 6, 10, 'A', '', '2025-12-19 14:24:48'),
(28, 18, 1, 'Al-Baqarah', 1, 100, 'A', 'Jangan lengah tetap semangat', '2026-01-12 21:13:57'),
(29, 19, 1, 'Al-Baqarah', 1, 100, 'A', 'Mantep jangan merasa sudah puas', '2026-01-12 21:14:47');

-- --------------------------------------------------------

--
-- Struktur dari tabel `ustadz`
--

CREATE TABLE `ustadz` (
  `id` int(11) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` varchar(20) DEFAULT 'ustadz',
  `status` varchar(20) DEFAULT 'Aktif'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `ustadz`
--

INSERT INTO `ustadz` (`id`, `nama`, `username`, `password`, `role`, `status`) VALUES
(1, 'Ustadz Ahmad', 'Ahmad', 'pbkdf2:sha256:1000000$jqh3UMb9TCYFglJq$216d262c24065b8cb0455f96dd8f01dde43f61976ad31603aab8678c26dbcd2b', 'ustadz', 'Aktif'),
(2, 'Ustadzah Fatimah', NULL, NULL, 'ustadz', 'Aktif'),
(4, 'Administrator', 'admin', 'pbkdf2:sha256:1000000$YZ4UTGmS8RKJ7i5p$9bc9500bcd234ac8be663e74f505379f18c556e5c419f231f097c4a8a6c187d1', 'admin', 'Aktif'),
(6, 'Nurul Hidayat', 'Hidayat', 'pbkdf2:sha256:1000000$B4cTVkRIJuY8H7Gi$cd6127b0d5ed68cbd7e7c6795c32faa276b6ddc61cfbc715ea3c66c015dc687e', 'ustadz', 'Aktif');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `absensi`
--
ALTER TABLE `absensi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `santri_id` (`santri_id`),
  ADD KEY `ustadz_id` (`ustadz_id`);

--
-- Indeks untuk tabel `konfigurasi`
--
ALTER TABLE `konfigurasi`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `santri`
--
ALTER TABLE `santri`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ustadz_id` (`ustadz_id`);

--
-- Indeks untuk tabel `setoran`
--
ALTER TABLE `setoran`
  ADD PRIMARY KEY (`id`),
  ADD KEY `santri_id` (`santri_id`),
  ADD KEY `ustadz_id` (`ustadz_id`);

--
-- Indeks untuk tabel `ustadz`
--
ALTER TABLE `ustadz`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `absensi`
--
ALTER TABLE `absensi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT untuk tabel `konfigurasi`
--
ALTER TABLE `konfigurasi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `santri`
--
ALTER TABLE `santri`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT untuk tabel `setoran`
--
ALTER TABLE `setoran`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT untuk tabel `ustadz`
--
ALTER TABLE `ustadz`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `absensi`
--
ALTER TABLE `absensi`
  ADD CONSTRAINT `absensi_ibfk_1` FOREIGN KEY (`santri_id`) REFERENCES `santri` (`id`),
  ADD CONSTRAINT `absensi_ibfk_2` FOREIGN KEY (`ustadz_id`) REFERENCES `ustadz` (`id`);

--
-- Ketidakleluasaan untuk tabel `santri`
--
ALTER TABLE `santri`
  ADD CONSTRAINT `santri_ibfk_1` FOREIGN KEY (`ustadz_id`) REFERENCES `ustadz` (`id`);

--
-- Ketidakleluasaan untuk tabel `setoran`
--
ALTER TABLE `setoran`
  ADD CONSTRAINT `setoran_ibfk_1` FOREIGN KEY (`santri_id`) REFERENCES `santri` (`id`),
  ADD CONSTRAINT `setoran_ibfk_2` FOREIGN KEY (`ustadz_id`) REFERENCES `ustadz` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
