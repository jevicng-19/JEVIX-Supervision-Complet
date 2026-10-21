CREATE DATABASE IF NOT EXISTS jevix;
USE jevix;

-- TABLE DES ADMINISTRATEURS

CREATE TABLE `administrateurs` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('superadmin','admin') NOT NULL DEFAULT 'admin',
  `date_creation` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- TABLE DES MACHINES

CREATE TABLE `machines` (
  `id` int(11) NOT NULL,
  `hostname` varchar(100) DEFAULT NULL,
  `username` varchar(100) DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `os` varchar(100) DEFAULT NULL,
  `os_version` varchar(100) DEFAULT NULL,
  `architecture` varchar(50) DEFAULT NULL,
  `cpu_percent` float DEFAULT NULL,
  `cpu_cores` int(11) DEFAULT NULL,
  `ram_total_gb` float DEFAULT NULL,
  `ram_used_percent` float DEFAULT NULL,
  `ram_available_gb` float DEFAULT NULL,
  `disk_total_gb` float DEFAULT NULL,
  `disk_used_percent` float DEFAULT NULL,
  `disk_free_gb` float DEFAULT NULL,
  `bytes_sent` bigint(20) DEFAULT NULL,
  `bytes_recv` bigint(20) DEFAULT NULL,
  `process_count` int(11) DEFAULT NULL,
  `battery_percent` float DEFAULT NULL,
  `battery_plugged` tinyint(1) DEFAULT NULL,
  `last_update` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- TABLE DES ALERTES

CREATE TABLE `alertes` (
  `id` int(11) NOT NULL,
  `machine_id` int(11) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `gravite` enum('FAIBLE','MOYEN','ELEVE','CRITIQUE') DEFAULT NULL,
  `valeur` varchar(100) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `statut` enum('NOUVELLE','EN_COURS','RESOLUE') DEFAULT 'NOUVELLE',
  `date_prise_en_charge` datetime DEFAULT NULL,
  `admin_id` int(11) DEFAULT NULL,
  `diagnostic` text DEFAULT NULL,
  `date_detection` datetime DEFAULT current_timestamp(),
  `date_resolution` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- TABLE JOURNAL (Historique)

CREATE TABLE `journal` (
  `id` int(11) NOT NULL,
  `admin_id` int(11) DEFAULT NULL,
  `action` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `date_action` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



-- Index pour les tables déchargées

--
-- Index pour la table `administrateurs`
--
ALTER TABLE `administrateurs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Index pour la table `alertes`
--
ALTER TABLE `alertes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `machine_id` (`machine_id`),
  ADD KEY `admin_id` (`admin_id`);

--
-- Index pour la table `journal`
--
ALTER TABLE `journal`
  ADD PRIMARY KEY (`id`),
  ADD KEY `admin_id` (`admin_id`);

--
-- Index pour la table `machines`
--
ALTER TABLE `machines`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `administrateurs`
--
ALTER TABLE `administrateurs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `alertes`
--
ALTER TABLE `alertes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `journal`
--
ALTER TABLE `journal`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `machines`
--
ALTER TABLE `machines`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `alertes`
--
ALTER TABLE `alertes`
  ADD CONSTRAINT `alertes_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `alertes_ibfk_2` FOREIGN KEY (`admin_id`) REFERENCES `administrateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `journal`
--
ALTER TABLE `journal`
  ADD CONSTRAINT `journal_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `administrateurs` (`id`) ON DELETE SET NULL;
COMMIT;
