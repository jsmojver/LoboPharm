use diocles;
-- phpMyAdmin SQL Dump
-- version 3.4.5deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Oct 09, 2011 at 01:55 AM
-- Server version: 5.1.58
-- PHP Version: 5.3.8-2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `diocles`
--

--
-- Table structure for table `depo_depo`
--

CREATE TABLE IF NOT EXISTS `depo_depo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `naziv` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=11 ;

--
-- Dumping data for table `depo_depo`
--

INSERT INTO `depo_depo` (`id`, `naziv`) VALUES
(1, 'Austrija'),
(2, 'Njemačka'),
(3, 'Slovenija'),
(4, 'Švicarska'),
(5, 'Italija'),
(6, 'Amerika'),
(7, 'Francuska'),
(8, 'Bosna i Hercegovina'),
(9, 'Španjolska'),
(10, 'Nizozemska');

-- --------------------------------------------------------

--
-- Table structure for table `depo_djelatnik`
--

CREATE TABLE IF NOT EXISTS `depo_djelatnik` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `ime` varchar(64) NOT NULL,
  `prezime` varchar(64) NOT NULL,
  `nadimak` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `depo_lijek`
--

CREATE TABLE IF NOT EXISTS `depo_lijek` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `naziv` varchar(256) NOT NULL,
  `cijena` decimal(12,2) DEFAULT NULL,
  `depo_id` int(11) NOT NULL,
  `stanje` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `depo_lijek_e2e91dba` (`depo_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=340 ;

--
-- Dumping data for table `depo_lijek`
--

INSERT INTO `depo_lijek` (`id`, `naziv`, `cijena`, `depo_id`, `stanje`) VALUES
(1, 'Aethoxysklerol 0,5 %', '14.80', 1, 13),
(2, 'Aethoxysklerol 1%', '16.96', 1, 12),
(3, 'Aethoxysklerol 2%', '17.56', 1, 10),
(4, 'Aethoxysklerol 3%', '19.00', 1, 10),
(5, 'Aknemycin Hidro 1%', '6.48', 1, 0),
(6, 'Akneroxid 5% 50 g', '6.06', 1, 24),
(7, 'Aknichtol lotio', '5.68', 1, 17),
(8, 'Aktiferrin tropfen', '1.90', 1, 13),
(9, 'Aldiamed mundgel 50 g', '7.95', 2, 9),
(10, 'Artane 5 mg 100 tbl', '38.70', 2, 6),
(11, 'Atarax 25 mg 50 tbl', '7.52', 1, 7),
(13, 'Babynos', '4.58', 1, 0),
(14, 'Benzaknen 10% gel 30 g', '5.10', 1, 24),
(15, 'Benzaknen 5% gel 30 g', '3.80', 1, 20),
(16, 'Broncho-Vaxom 3,5 mg', '19.76', 1, 9),
(17, 'Broncho-Vaxom 7 mg', '28.20', 1, 3),
(18, 'Ciloxan 5 ml Aus.', '5.32', 1, 3),
(19, 'Colchicin tbl.', '7.42', 1, 12),
(20, 'Depakine Chrono 250 mg Ret', '10.06', 1, 34),
(21, 'Depakine Chrono 50 mg', '3.52', 1, 31),
(22, 'Diamox 100 tbl', '18.38', 1, 7),
(23, 'Diferin Gel', '12.26', 1, 19),
(24, 'Doderline', '6.40', 1, 12),
(25, 'Eryaknen 4% Gel 30 g', '6.68', 1, 13),
(26, 'Essentiale F 100 tbl', '29.92', 1, 9),
(27, 'Eudyna Creme', '4.48', 1, 0),
(28, 'Gentax AT 5 ml', '3.88', 1, 4),
(29, 'Hadensa salbe 42 g', '5.10', 1, 26),
(30, 'Hadensa supp á 12 st', '4.94', 1, 5),
(31, 'Hepavit 2500', '3.52', 1, 0),
(32, 'Lariam 250 mg', '46.42', 1, 19),
(33, 'Minostad 50 mg 30 kps', '7.76', 1, 77),
(34, 'Neurobion Amp', '2.68', 1, 27),
(36, 'Neurobion F 20 tbl', '3.14', 1, 35),
(37, 'Oleovit Augensalbe', '2.82', 1, 18),
(38, 'Oleovit D3 Tropfen', '4.12', 1, 19),
(39, 'Patentex Oval Ovula 12 st', '10.12', 1, 8),
(40, 'Pilocarpin 1% AT 10 ml', '6.88', 1, 0),
(41, 'Pilocarpin 2% 10 ml austrijski', '8.62', 1, 0),
(42, 'Resochin tbl', '6.42', 1, 12),
(43, 'Rheumesser 3x3 ml amp.', '8.36', 1, 26),
(44, 'Selsun Med.Shampoo 120 ml', '9.76', 1, 0),
(45, 'Sibelium 10 mg', '16.38', 1, 12),
(46, 'Sintrom', '5.00', 7, 18),
(47, 'Thiamazol 20 mg 50 tbl', '5.88', 1, 9),
(48, 'Thrombo ASS 100 mg', '5.48', 1, 19),
(49, 'Unichol', '4.68', 1, 0),
(50, 'Uralyt U granulat', '24.48', 1, 12),
(51, 'Verumal lot 13 ml', '12.40', 1, 8),
(52, 'Volon A 10 mg', '3.06', 1, 11),
(53, 'Zoroxin AT', '5.28', 1, 2),
(54, 'Zyrtec Losung', '6.42', 1, 9),
(55, 'Adavin 10 mg', '5.90', 3, 7),
(56, 'Aldactone 50 mg SLO 20 st', '7.70', 3, 23),
(57, 'Aldara 5% krema slovenska', '99.80', 3, 4),
(58, 'Alkeran tbl 25x2 mg', '6.30', 3, 0),
(59, 'Angised tbl 100x0,5 mg', '4.50', 3, 19),
(60, 'Bilobil kps', '6.70', 3, 0),
(61, 'Cialis 20 mg 4 tbl', '70.00', 3, 8),
(62, 'Cyclo-Proginova', '8.10', 3, 13),
(63, 'Dicynone tbl 30x250 mg', '6.50', 3, 0),
(65, 'Doxilex kps 500 mg', '9.00', 3, 0),
(66, 'Flixonase SLO', '34.00', 3, 7),
(68, 'Lacryvisc gel 10 g', '6.00', 3, 9),
(69, 'Lasix tbl', '2.00', 3, 8),
(70, 'Leukeran 2 mg 25 tbl (SLO)', '16.00', 3, 15),
(72, 'Modolex mast', '9.50', 3, 7),
(73, 'Naklofen duo 75 mg', '2.80', 3, 0),
(74, 'Omnic kps', '35.00', 3, 0),
(75, 'Plavix tbl', '51.90', 3, 3),
(76, 'Propomed C pastile', '2.50', 3, 0),
(77, 'Puri - nethol 50 mg', '5.00', 3, 6),
(78, 'Quinax kapi', '8.50', 3, 22),
(79, 'Redergin 1,5 mg', '5.40', 3, 27),
(80, 'Redergin 4,5 mg', '8.00', 3, 0),
(81, 'Redergin kapi', '7.20', 3, 5),
(82, 'Rivotril 0,5 mg 50 tbl SLOVENIJA', '5.00', 3, 10),
(83, 'Rivotril 2 mg 30 tbl SLOVENIJA', '5.00', 3, 12),
(84, 'Stediril M', '3.00', 3, 4),
(85, 'Tametil', '7.00', 3, 1),
(86, 'Tears Naturale 15 ml', '5.00', 3, 0),
(87, 'Tenzimet tbl', '11.50', 3, 14),
(88, 'Torecan 6,5 mg', '5.50', 3, 14),
(89, 'Torecan supp', '4.80', 3, 0),
(90, 'Venter tbl', '10.60', 3, 6),
(91, 'Ventolin inh.otop.', '8.10', 3, 0),
(92, 'Verolax tbl', '5.00', 3, 0),
(94, 'Calcium-Magnesium caps. 180', '34.00', 6, 0),
(95, 'Cellfood DNA/RNA spray 30 ml', '80.00', 6, 0),
(96, 'Denorex Veliki', '23.00', 6, 14),
(97, 'Esmolol HCl inj. 10x10 mg/ml', '360.00', 6, 0),
(98, 'Labetalol HCl injection 5 mg/ml', '5.50', 6, 0),
(99, 'MG 217 Lotion', '0.00', 6, 0),
(100, 'Nitro-Bid 30 g', '11.00', 6, 0),
(101, 'Nitro-Bid ointment 2% á 60 g', '17.00', 6, 0),
(102, 'Ocuvite', '32.00', 6, 6),
(103, 'Omega 3.6.9 junior 90 st', '52.00', 6, 0),
(104, 'Profibe powder 380 g', '39.00', 6, 0),
(105, 'Racepinephrine Liq. 2,25%', '90.00', 6, 24),
(106, 'RESTASYS kapi 0,05% 32x0,4 ml', '307.90', 6, 4),
(107, 'Skinceuticals 20 serum 30 ml', '150.00', 6, 0),
(108, 'AULIN granulat', '5.90', 5, 18),
(109, 'Coumadin 5 mg Italija', '2.89', 5, 0),
(110, 'De-Nol 120 mg 40 comp.', '13.96', 5, 23),
(111, 'Konakion tbl', '5.15', 5, 0),
(112, 'Lantigen B', '17.85', 5, 17),
(113, 'Largactil 100 mg 20 comp.', '3.00', 5, 13),
(114, 'Merbromina sol 30 ml', '4.39', 5, 6),
(115, 'OZOPULMIN bambini supp.', '8.65', 5, 38),
(116, 'OZOPULMIN lattanti supp.', '7.05', 5, 36),
(117, 'Suprefact Spray ITALIJA', '55.00', 5, 0),
(118, 'Zentel', '9.01', 5, 0),
(119, 'Urodine tropfen', '5.50', 4, 0),
(120, 'Vitamin A amp. 10x1 ml', '15.19', 4, 12),
(121, 'Coumadin 2 mg Francuska', '3.73', 7, 0),
(122, 'Esperal 500 mg', '4.13', 7, 0),
(123, 'ABC Hansaplast 1/1', '3.95', 2, 24),
(124, 'ABC Hansaplast 2', '9.17', 2, 17),
(125, 'ABC Warme creme', '8.76', 2, 13),
(126, 'Actihaemyl', '8.89', 2, 19),
(127, 'Agiolax Granulat', '10.12', 1, 6),
(128, 'Ajona', '1.49', 2, 20),
(129, 'Antikataraktikum', '14.34', 2, 0),
(130, 'Artane 2 mg', '25.95', 2, 3),
(131, 'Aspirin P 100 mg', '11.80', 2, 13),
(132, 'Aspirin P 300 mg', '5.85', 2, 13),
(133, 'Bepanthen salbe 10 g', '5.78', 2, 20),
(134, 'Chloralhydrat Rectiole', '14.26', 2, 0),
(135, 'Cornere gel 10 g', '5.20', 2, 28),
(136, 'Cornere gel 3x10 g', '10.75', 2, 14),
(137, 'Cromoglicin Heumann AT', '4.39', 2, 10),
(138, 'Cromoglicin Heumann Spray', '6.37', 2, 13),
(139, 'Dentinox gel', '4.79', 2, 0),
(140, 'Echovist 200', '78.64', 1, 0),
(141, 'Emla Creme + 2 Tegadermpf', '7.62', 2, 6),
(142, 'Finalgon extra salbe', '8.90', 1, 9),
(143, 'Gaviscon Susp 200 ml', '11.80', 2, 8),
(144, 'Glandosane', '9.38', 1, 5),
(145, 'Grippostad c', '8.95', 2, 3),
(146, 'Gynodian depot 3 st', '34.55', 2, 8),
(147, 'Hepa gel 30000', '7.84', 2, 13),
(148, 'Hepa gel 60000', '11.96', 2, 9),
(149, 'Hepa salbe 30000', '7.84', 2, 13),
(150, 'Hepa salbe 60000', '11.96', 2, 15),
(151, 'Kendural C', '14.95', 2, 3),
(152, 'Malarone', '69.30', 1, 17),
(153, 'Methyldopa Stada 250 mg 100 st', '23.90', 2, 0),
(154, 'Midro Tee 48 g', '3.32', 2, 28),
(155, 'MOBILAT Salbe 100 g', '8.88', 1, 11),
(156, 'Nitrolingual kps', '3.58', 1, 10),
(157, 'Ortho-gynest vag.crem. 80 g', '10.38', 1, 0),
(158, 'Ovestin Creme 50 g', '15.10', 2, 3),
(159, 'Reisetabletten', '3.00', 2, 9),
(160, 'Rowachol 100', '11.63', 2, 19),
(161, 'Rowatinex 100', '11.63', 2, 7),
(162, 'Solcoseryl AG', '4.94', 1, 11),
(163, 'Toplomjer', '6.00', 2, 37),
(164, 'Uro Tablinen 50 tbl', '9.60', 2, 10),
(165, 'Vidisic AG 10 g', '4.95', 2, 25),
(166, 'Vidisic AG 3x10 g', '10.20', 2, 15),
(167, 'Vitadral 50 ml', '13.99', 2, 12),
(168, 'Vitamin B1 amp. RATIO', '3.58', 2, 7),
(169, 'Vitamin B6 amp. RATIO', '2.38', 2, 12),
(170, 'Vitamin C Rot.Amp.', '5.28', 2, 11),
(171, 'Nomigren', '10.00', 8, 245),
(172, 'Testosteron depo 5x1 ml', '20.00', 8, 83),
(174, 'Lariam 250 mg Italija', '53.06', 5, 0),
(175, 'Furantoina sirup', '8.00', 9, 28),
(176, 'gamalon', '25.00', 1, 10),
(177, 'Polygynax', '6.43', 7, 183),
(178, 'Sintrom Austrija', '5.36', 1, 0),
(179, 'Ozopulmin Adulti', '10.91', 5, 21),
(180, 'Vagitorije sa kantarionovim uljem', '8.00', 8, 0),
(181, 'Muscoflex 4 mg', '8.00', 8, 0),
(185, 'Vitamin B6 20 mg', '2.86', 2, 2),
(187, 'Tamiflu 75 mg kps', '37.25', 2, 0),
(188, 'Sermion 10 mg  20 st', '6.68', 1, 0),
(189, 'Ditamin tbl', '3.40', 3, 10),
(190, 'Mysteclin Ovula 6st', '4.80', 1, 54),
(191, 'Saridon', '4.22', 1, 0),
(192, 'Utrogestan 100 mg', '11.52', 1, 0),
(193, 'Avamigran', '6.58', 1, 0),
(195, 'Esafosfina 10g/100ml', '30.00', 5, 0),
(197, 'Amphotericin B 50 mg', '56.26', 1, 0),
(198, 'Lido Hyal B amp 2ml', '3.00', 4, 0),
(199, 'Preductal MR', '16.80', 3, 0),
(200, 'Tardyferon Fol', '13.32', 2, 8),
(201, 'Cantabilin', '8.98', 7, 10),
(202, 'Navelbine 10 mg', '58.43', 2, 0),
(203, 'Navelbine 10 mg  Emra', '50.02', 2, 5),
(205, 'Hyalgan 20 mg / 2 ml', '61.00', 5, 5),
(206, 'Moditen 1 mg', '4.30', 3, 4),
(207, 'Natulan 50 mg', '280.00', 10, 0),
(208, 'Apilepsin', '15.60', 3, 0),
(209, 'Voltaren dispers  20 tbl', '4.20', 1, 14),
(215, 'Aldometil 250 mg', '5.11', 5, 30),
(216, 'Omnic Ocas 0,4 mg', '19.80', 3, 0),
(219, 'Fluad Fertigspritze', '22.10', 1, 0),
(225, 'Vaxygrip', '13.40', 1, 0),
(226, 'Canesten lsg', '5.00', 2, 11),
(235, 'diamox 20 tbl.', '4.78', 1, 82),
(237, 'Multaq 400 mg', '375.00', 6, 0),
(254, 'Microklist 4 st', '6.58', 1, 0),
(255, 'Mexitil 200 mg', '12.68', 5, 0),
(256, 'Echovist 300', '104.96', 2, 0),
(257, 'Aldometil 500 mg', '10.15', 2, 0),
(258, 'Ergenyl Chrono 250 mg', '9.09', 2, 0),
(259, 'Pankreoflat 50 drg', '13.12', 1, 7),
(260, 'Catapresan 0,150 mg', '17.90', 1, 0),
(262, 'Mexitil 200 mg 100 st', '71.34', 2, 0),
(263, 'Labetalol amp', '5.50', 6, 50),
(264, 'Pancillin 800 000 i.j.', '30.00', 8, 8),
(265, 'Suprefact spray', '55.00', 10, 5),
(266, 'Propranolol 40 mg', '4.80', 3, 0),
(267, 'Bengay ultra stranght', '15.56', 6, 5),
(268, 'Polygynax Vag. 6 kom', '8.00', 8, 0),
(270, 'Phenylephrin 1 % amp', '120.00', 6, 4),
(271, 'Infanrix IPV+HIB', '58.25', 2, 5),
(272, 'Synvisc Amp', '293.53', 2, 5),
(273, 'Diprophos 1 ml Amp', '9.68', 1, 0),
(274, 'Phenylephrine amp.10mg/ml', '120.00', 6, 0),
(275, 'Labetalol amp.5mg/ml', '5.50', 6, 0),
(276, 'Iruxol mast', '28.00', 5, 0),
(278, 'Seldiar', '3.35', 3, 5),
(279, 'Intrafer Tropfen', '7.29', 5, 1),
(281, 'Cetrotide 0,25 mg', '60.00', 3, 14),
(282, 'Microkl. Glicerolo', '5.86', 5, 0),
(284, 'A.T.losung 90 ml', '54.52', 2, 9),
(285, 'Alfa', '8.11', 5, 1),
(286, 'Fibrase 50 mg', '21.40', 5, 0),
(287, 'Clomid 50 mg', '12.00', 5, 24),
(288, 'Cafergot 2 mg+100 mg supp', '5.90', 5, 0),
(289, 'Emser Nasendusche', '14.31', 2, 5),
(290, 'Armour Thyroid 60 mg', '35.74', 6, 5),
(291, 'Excedrin Migraine', '20.38', 6, 5),
(292, 'Oki 80 mg', '5.70', 5, 0),
(293, 'Denorex mali', '15.00', 6, 0),
(294, 'Brunac 5% AT', '8.65', 5, 15),
(295, 'Dexa-Gentamycin Kombi', '15.70', 1, 8),
(296, 'Gentamycin AG 5g', '12.00', 1, 4),
(297, 'Gentamycin AT 5 ml', '12.00', 1, 5),
(298, 'Blephasol Lotio 100 ml', '11.40', 1, 0),
(280, 'Armour Thyroid 30 mg', '32.18', 6, 10),
(299, 'Voltaren Ophta AT 5 ml', '15.94', 1, 4),
(302, 'Protopic 0,1 % Salbe', '25.70', 1, 9),
(303, 'Protopic 0,03 % Salbe', '23.12', 1, 8),
(304, 'Skinoren Gel 15 %', '25.00', 1, 6),
(305, 'Laticort 0,1% Crema', '12.82', 2, 5),
(306, 'Laticort 0,1% Salbe', '12.82', 2, 9),
(307, 'Duac Akne Gel', '28.35', 2, 7),
(308, 'Infectodell Losung', '11.40', 2, 6),
(309, 'Airol Losung', '17.47', 2, 12),
(310, 'Widmer Efadermin Salbe', '11.96', 2, 4),
(311, 'Dermasence Zincutan Schaum', '12.20', 2, 2),
(312, 'Physiogel A.I. Creme', '19.90', 2, 5),
(313, 'Physiogel A.I. Lotion', '27.90', 2, 5),
(314, 'Zineryt Losung', '25.48', 2, 8),
(315, 'Clarelux Schaum', '22.82', 2, 4),
(316, 'Guttaplast 1 st', '5.03', 2, 11),
(317, 'Zactoline Creme', '20.47', 2, 1),
(318, 'Fucidine Creme', '11.60', 2, 5),
(319, 'Linola Sept Creme', '6.59', 2, 5),
(320, 'Systane balance AT 10 ml', '23.76', 6, 4),
(321, 'Floxapen 500 mg', '18.80', 1, 7),
(322, 'Ficotril Augensalbe 0,5 %', '12.47', 2, 10),
(323, 'Pigmanorm Creme', '19.81', 2, 6),
(324, 'Dexagel', '13.82', 2, 5),
(325, 'Atropin Sulfat 0,5 %', '17.20', 3, 76),
(326, 'Atropin Sulfat 1%', '31.00', 3, 76),
(327, 'Quinax bez ambalaze', '8.50', 3, 1),
(328, 'Propranolol bez ambalaze', '4.80', 3, 8),
(329, 'Aldactone 25 mg', '3.80', 3, 7),
(331, 'Plaquenil 200 mg', '10.00', 5, 14),
(333, 'Catacol AT 10 ml', '10.98', 7, 48),
(334, 'Tylenol 100 st', '21.38', 6, 2),
(335, 'Diprostene 1 ml', '11.15', 7, 4),
(336, 'Volon A 40 mg', '8.98', 1, 1),
(337, 'Rechtsregulat 350 ml', '44.00', 2, 0),
(338, 'Flosteron amp.', '4.50', 3, 5),
(339, 'Almased 500 g', '27.00', 2, 19),
(301, 'Bepanthen 10 g dr. Tafra', '5.78', 2, 0),
(300, 'Bepanthen 5 g dr. Tafra', '3.45', 2, 14),
(93, '      Asper cream', '16.00', 6, 3),
(35, 'Neurobion F 100 tbl', '13.16', 1, 70);

-- --------------------------------------------------------

--
-- Table structure for table `depo_posiljka`
--

CREATE TABLE IF NOT EXISTS `depo_posiljka` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `broj` int(11) NOT NULL,
  `datum` datetime NOT NULL,
  `zaduzio_id` int(11) NOT NULL,
  `lijekovi_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `depo_posiljka_3a6e082d` (`zaduzio_id`),
  KEY `depo_posiljka_6ba8e823` (`lijekovi_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `depo_posiljkalijek`
--

CREATE TABLE IF NOT EXISTS `depo_posiljkalijek` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lijek_id` int(11) NOT NULL,
  `kolicina` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lijek_id` (`lijek_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `depo_zahtjev`
--

CREATE TABLE IF NOT EXISTS `depo_zahtjev` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lijek_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `depo_zahtjev_c5d9600` (`lijek_id`),
  KEY `depo_zahtjev_fbfc09f1` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_fbfc09f1` (`user_id`),
  KEY `django_admin_log_e4470c6e` (`content_type_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=15 ;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `user_id`, `content_type_id`, `object_id`, `object_repr`, `action_flag`, `change_message`) VALUES
(1, '2011-10-09 01:51:44', 1, 10, '1', 'Austrija', 1, ''),
(2, '2011-10-09 01:51:49', 1, 10, '2', 'Njemačka', 1, ''),
(3, '2011-10-09 01:51:51', 1, 10, '3', 'Slovenija', 1, ''),
(4, '2011-10-09 01:51:54', 1, 10, '4', 'Švicarska', 1, ''),
(5, '2011-10-09 01:52:01', 1, 10, '5', 'Italija', 1, ''),
(6, '2011-10-09 01:52:04', 1, 10, '6', 'Amerika', 1, ''),
(7, '2011-10-09 01:52:08', 1, 10, '7', 'Francuska', 1, ''),
(8, '2011-10-09 01:52:14', 1, 10, '8', 'Bosna i Hercegovina', 1, ''),
(9, '2011-10-09 01:52:18', 1, 10, '9', 'Španjolska', 1, ''),
(10, '2011-10-09 01:52:22', 1, 10, '10', 'Nizozemska', 1, ''),
(11, '2011-10-09 01:54:39', 1, 11, '5', 'Aknemycin Hidro 1%', 2, 'Promijenjeno naziv.'),
(12, '2011-10-09 01:54:51', 1, 11, '4', 'Aethoxysklerol 3%', 2, 'Promijenjeno naziv.'),
(13, '2011-10-09 01:55:02', 1, 11, '1', 'Aethoxysklerol 0,5 %', 2, 'Promijenjeno naziv.'),
(14, '2011-10-09 01:55:09', 1, 11, '2', 'Aethoxysklerol 1%', 2, 'Promijenjeno naziv.');

-- --------------------------------------------------------

--
-- Table structure for table `meds_dobavljac`
--

CREATE TABLE IF NOT EXISTS `meds_dobavljac` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `naziv` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `meds_lijek`
--

CREATE TABLE IF NOT EXISTS `meds_lijek` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `SortNr` bigint(20) NOT NULL,
  `ZoNr` bigint(20) NOT NULL,
  `name` varchar(96) NOT NULL,
  `slug` varchar(64) NOT NULL,
  `kolicina` varchar(8) NOT NULL,
  `jedinice` varchar(8) NOT NULL,
  `std_kolicina` varchar(8) NOT NULL,
  `kratica_dobavljaca` varchar(10) NOT NULL,
  `apoek` bigint(20) NOT NULL,
  `apovk` bigint(20) NOT NULL,
  `kvaek` bigint(20) NOT NULL,
  `hervk` bigint(20) NOT NULL,
  `ATCCode` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meds_lijek_52094d6e` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
