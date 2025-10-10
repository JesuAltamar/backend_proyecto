-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 03-10-2025 a las 08:26:27
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `alegra`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analisis_sentimientos`
--

CREATE TABLE `analisis_sentimientos` (
  `id` int(11) NOT NULL,
  `chat_interaccion_id` int(11) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `sentimiento` enum('positivo','neutral','negativo') NOT NULL,
  `nivel_riesgo` enum('ninguno','bajo','moderado','alto','critico') DEFAULT 'ninguno',
  `palabras_clave` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`palabras_clave`)),
  `fecha_analisis` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `avatar_config`
--

CREATE TABLE `avatar_config` (
  `id` int(11) NOT NULL,
  `max_file_size` int(11) DEFAULT 5242880 COMMENT 'Tama?o m?ximo en bytes (5MB por defecto)',
  `allowed_extensions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT '["jpg", "jpeg", "png", "gif", "webp"]' CHECK (json_valid(`allowed_extensions`)),
  `upload_path` varchar(255) DEFAULT 'uploads/avatars',
  `base_url` varchar(255) DEFAULT 'http://backendproyecto-producción-4a8d.up.railway.app',
  `compression_quality` int(11) DEFAULT 85 COMMENT 'Calidad de compresi?n (1-100)',
  `max_width` int(11) DEFAULT 800 COMMENT 'Ancho m?ximo en p?xeles',
  `max_height` int(11) DEFAULT 800 COMMENT 'Alto m?ximo en p?xeles',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `avatar_config`
--

INSERT INTO `avatar_config` (`id`, `max_file_size`, `allowed_extensions`, `upload_path`, `base_url`, `compression_quality`, `max_width`, `max_height`, `created_at`, `updated_at`) VALUES
(1, 5242880, '[\"jpg\", \"jpeg\", \"png\", \"gif\", \"webp\"]', 'uploads/avatars', 'http://backendproyecto-producción-4a8d.up.railway.app', 85, 800, 800, '2025-09-30 23:25:29', '2025-09-30 23:25:29');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `avatar_logs`
--

CREATE TABLE `avatar_logs` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `action` enum('upload','delete','update') NOT NULL,
  `old_avatar_url` varchar(500) DEFAULT NULL,
  `new_avatar_url` varchar(500) DEFAULT NULL,
  `file_size` int(11) DEFAULT NULL COMMENT 'Tama?o del archivo en bytes',
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chat_analytics`
--

CREATE TABLE `chat_analytics` (
  `id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `sentimiento_positivo` int(11) DEFAULT 0,
  `sentimiento_neutral` int(11) DEFAULT 0,
  `sentimiento_negativo` int(11) DEFAULT 0,
  `total_mensajes` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `chat_analytics`
--

INSERT INTO `chat_analytics` (`id`, `fecha`, `sentimiento_positivo`, `sentimiento_neutral`, `sentimiento_negativo`, `total_mensajes`, `created_at`) VALUES
(1, '2025-09-30', 5, 5, 3, 13, '2025-09-30 17:11:01'),
(2, '2025-09-29', 4, 4, 2, 10, '2025-09-30 17:11:01'),
(3, '2025-09-28', 6, 2, 2, 10, '2025-09-30 17:11:01'),
(7, '2025-10-02', 0, 2, 0, 2, '2025-10-02 15:18:15');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chat_interacciones`
--

CREATE TABLE `chat_interacciones` (
  `id` int(11) NOT NULL,
  `session_id` varchar(255) NOT NULL,
  `mensaje` text NOT NULL,
  `remitente` enum('user','bot') NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_id` int(11) DEFAULT NULL,
  `is_crisis` tinyint(1) DEFAULT 0,
  `crisis_level` enum('none','moderate','severe') DEFAULT 'none',
  `sentimiento` varchar(20) DEFAULT 'neutral',
  `tema` varchar(100) DEFAULT NULL,
  `palabras_clave` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `chat_interacciones`
--

INSERT INTO `chat_interacciones` (`id`, `session_id`, `mensaje`, `remitente`, `fecha`, `usuario_id`, `is_crisis`, `crisis_level`, `sentimiento`, `tema`, `palabras_clave`) VALUES
(1, '1758849363836', 'hola', 'user', '2025-09-26 01:16:09', 0, 0, 'none', 'neutral', NULL, NULL),
(2, '1758849800952', 'hola', 'user', '2025-09-26 01:23:27', 0, 0, 'none', 'neutral', NULL, NULL),
(3, '1758849800952', 'Hola, estoy aqui para ayudarte, soy tu psicóloga virtual. Cuéntame, ¿cómo te sientes hoy?', 'bot', '2025-09-26 01:23:28', 0, 0, 'none', 'neutral', NULL, NULL),
(4, '1758897679603', 'me siento mal', 'user', '2025-09-26 14:41:27', 0, 0, 'none', 'neutral', NULL, NULL),
(5, '1758897679603', 'Hola, estoy aqui para ayudarte, soy tu psicóloga virtual. Cuéntame, ¿cómo te sientes hoy?', 'bot', '2025-09-26 14:41:28', 0, 0, 'none', 'neutral', NULL, NULL),
(6, '1759153894544', 'hola', 'user', '2025-09-29 13:51:41', 0, 0, 'none', 'neutral', NULL, NULL),
(7, '1759153894544', 'Hola, estoy aqui para ayudarte, soy tu psicóloga virtual. Cuéntame, ¿cómo te sientes hoy?', 'bot', '2025-09-29 13:51:43', 0, 0, 'none', 'neutral', NULL, NULL),
(8, '1759204264830', 'triste', 'user', '2025-09-30 03:51:21', NULL, 0, 'none', 'neutral', NULL, NULL),
(9, '1759204264830', 'Disculpa, tuve un problema técnico. Por favor intenta de nuevo o llama a la Línea 106 si necesitas ayuda urgente.', 'bot', '2025-09-30 03:51:22', NULL, 0, 'none', 'neutral', NULL, NULL),
(10, '1759204540655', 'muy triste', 'user', '2025-09-30 03:55:52', NULL, 0, 'none', 'neutral', NULL, NULL),
(11, '1759204540655', 'Disculpa, tuve un problema técnico. Por favor intenta de nuevo.', 'bot', '2025-09-30 03:55:53', NULL, 0, 'none', 'neutral', NULL, NULL),
(12, '1759204950293', 'deprimido no encuentro que hacer', 'user', '2025-09-30 04:02:58', NULL, 0, 'none', 'neutral', NULL, NULL),
(13, '1759204950293', 'Lamento mucho escuchar que te sientes deprimido y que no encuentras qué hacer. Es una sensación muy difícil y quiero que sepas que no estás solo en esto. Es valiente de tu parte expresarlo.\n\nTus sentimientos son válidos y es completamente normal sentirse así a veces. Estoy aquí para escucharte sin juzgar.\n\nSi en algún momento sientes que la situación te supera y necesitas hablar con alguien de inmediato, o simplemente quieres un espacio seguro para ser escuchado, hay profesionales disponibles las 24 horas del día. No tienes que cargar con esto solo/a.\n\nAquí tienes algunas líneas de ayuda en Colombia que pueden ofrecerte apoyo profesional en este momento:\n\n*   **Línea 106:** Atención en crisis 24/7\n*   **Línea 155:** Orientación psicológica\n*   **WhatsApp: +57 300 754 8933** (Línea Amiga Bogotá)\n*   También puedes encontrar más recursos en: [https://findahelpline.com](https://findahelpline.com)\n\n¿Hay algo más que quieras compartir sobre cómo te sientes o algo específico que te esté preocupando en este momento? Estoy aquí para escucharte.', 'bot', '2025-09-30 04:03:03', NULL, 0, 'none', 'neutral', NULL, NULL),
(14, '1759204950293', 'que me recomiendas cuando este triste?', 'user', '2025-09-30 04:07:40', NULL, 0, 'none', 'neutral', NULL, NULL),
(15, '1759204950293', 'Es una excelente pregunta y es muy valiente de tu parte buscar formas de manejar la tristeza. Cuando nos sentimos tristes, a menudo lo que más necesitamos es comprensión y herramientas suaves para navegar esas emociones.\n\nAquí tienes algunas recomendaciones que pueden ayudarte cuando te sientas triste:\n\n1.  **Permítete sentir la emoción:** A veces, intentamos reprimir la tristeza, pero darle espacio para que exista, sin juzgarla, puede ser el primer paso. No tienes que fingir que estás bien si no lo estás.\n2.  **Habla con alguien de confianza:** Compartir lo que sientes con un amigo, familiar o un profesional puede aliviar la carga. A veces, simplemente expresar en voz alta lo que nos pasa ya nos ayuda a procesarlo.\n3.  **Realiza una actividad que te consuele:** Puede ser escuchar tu música favorita, ver una película que te guste, leer un libro, tomar una bebida caliente, o simplemente acurrucarte con una manta. Pequeños gestos de autocuidado pueden hacer una gran diferencia.\n4.  **Muévete suavemente:** No necesitas hacer ejercicio intenso. Una caminata corta al aire libre, estiramientos suaves o incluso bailar un poco en casa pueden ayudar a liberar endorfinas y cambiar un poco la perspectiva.\n5.  **Practica la atención plena (mindfulness) o la respiración consciente:** Concéntrate en tu respiración por unos minutos, observa cómo entra y sale el aire de tu cuerpo. Esto puede ayudarte a anclarte en el presente y reducir la rumiación de pensamientos negativos.\n6.  **Escribe lo que sientes:** Llevar un diario o simplemente escribir libremente sobre tus pensamientos y emociones puede ser una forma muy efectiva de procesarlos y entenderlos mejor.\n7.  **Busca la luz natural:** Si es posible, sal un rato al sol o siéntate cerca de una ventana. La luz natural puede influir positivamente en el estado de ánimo.\n8.  **Establece límites:** A veces, cuando estamos tristes, es bueno tomar un descanso de las redes sociales, las noticias o situaciones que puedan aumentar tu malestar.\n\nRecuerda, estas son solo sugerencias y lo más importante es que seas amable y paciente contigo mismo/a. Si la tristeza es persistente, muy intensa o sientes que te está afectando significativamente en tu día a día, buscar el apoyo de un profesional de la salud mental puede ser de gran ayuda. Ellos pueden ofrecerte herramientas y estrategias personalizadas.\n\nY por supuesto, si en algún momento sientes que necesitas hablar con alguien de inmediato, las líneas de ayuda profesional están siempre disponibles:\n\n*   **Línea 106:** Atención en crisis 24/7\n*   **Línea 155:** Orientación psicológica\n*   **WhatsApp: +57 300 754 8933** (Línea Amiga Bogotá)\n\nEstoy aquí para escucharte si quieres compartir más sobre lo que te sucede o si hay algo más en lo que pueda apoyarte.', 'bot', '2025-09-30 04:07:48', NULL, 0, 'none', 'neutral', NULL, NULL),
(16, '1759214594760', 'mal siento ganas de hacerme daño', 'user', '2025-09-30 06:43:56', NULL, 0, 'none', 'neutral', NULL, NULL),
(17, '1759214594760', 'Siento mucho escuchar que te sientes así y que tienes ganas de hacerte daño. Es una carga muy pesada de llevar, y quiero que sepas que no estás solo/a en esto. Es valiente de tu parte compartir cómo te sientes.\n\nEn este momento, lo más importante es que busques apoyo inmediato. Hay personas que están listas y dispuestas a escucharte y ayudarte. Por favor, considera contactar una de estas líneas de ayuda en Colombia:\n\n*   **Línea 106:** Atención en crisis 24/7.\n*   **Línea 155:** Orientación psicológica.\n*   **WhatsApp: +57 300 754 8933** (Línea Amiga Bogotá).\n\nEstas líneas son confidenciales y están diseñadas para ofrecerte un espacio seguro donde puedas hablar y recibir el apoyo profesional que necesitas ahora mismo.\n\nEstoy aquí para escucharte, pero por favor, contacta a alguien de estas líneas. No tienes que enfrentar esto solo/a.', 'bot', '2025-09-30 06:44:00', NULL, 1, 'none', 'neutral', NULL, NULL),
(18, '1759215594616', 'muymal con desepero', 'user', '2025-09-30 07:00:09', NULL, 0, 'none', 'neutral', NULL, NULL),
(19, '1759215594616', 'Siento mucho escuchar que te sientes muy mal y con desespero. Es completamente válido sentirte así, y quiero que sepas que no estás solo/a en esto. Reconocer y expresar ese desespero es un primer paso muy valiente.\n\nCuando el desespero se vuelve tan intenso, es fundamental buscar apoyo profesional de inmediato. Por favor, considera contactar a las siguientes líneas de ayuda en Colombia, donde profesionales capacitados están listos para escucharte y ofrecerte el soporte que necesitas, las 24 horas del día:\n\n*   **Línea 106:** Atención de crisis 24/7\n*   **Línea 155:** Orientación psicológica\n*   **WhatsApp: +57 300 754 8933** (Línea Amiga Bogotá)\n*   También puedes encontrar más recursos en: [https://findahelpline.com](https://findahelpline.com)\n\nEstoy aquí para escucharte, si quieres compartir más sobre lo que sientes. Recuerda que no tienes que llevar esta carga solo/a.', 'bot', '2025-09-30 07:00:14', NULL, 0, 'none', 'neutral', NULL, NULL),
(20, '1759217229455', 'mal', 'user', '2025-09-30 07:27:20', NULL, 0, 'none', 'neutral', NULL, NULL),
(21, '1759217229455', 'Siento mucho escuchar que te sientes mal. Es completamente válido sentirse así, y estoy aquí para escucharte sin juicios.\n\nSi te sientes cómodo/a compartiendo, me gustaría saber un poco más sobre qué te hace sentir mal. No hay presión si no quieres, pero a veces hablar un poco ayuda.\n\nRecuerda que estoy aquí para apoyarte.', 'bot', '2025-09-30 07:27:24', NULL, 0, 'none', 'neutral', NULL, NULL),
(22, '1759234985830', 'me siento mal con ganas de hacerme daño', 'user', '2025-09-30 12:23:51', NULL, 0, 'none', 'neutral', NULL, NULL),
(23, '1759234985830', 'Lamento mucho, muchísimo, escuchar que te sientes así y que tienes ganas de hacerte daño. Sé que esa sensación es increíblemente difícil y dolorosa de llevar. Quiero que sepas que no estás solo/a con estos sentimientos.\n\nEs muy importante que busques apoyo ahora mismo. Por favor, comunícate con alguien que pueda brindarte ayuda profesional y escucharte en este momento tan difícil. Aquí tienes líneas de ayuda disponibles en Colombia, donde puedes hablar con profesionales que están listos para apoyarte:\n\n*   **Línea 106:** Atención de crisis 24/7. Puedes llamar en cualquier momento.\n*   **Línea 155:** Orientación psicológica.\n*   **WhatsApp: +57 300 754 8933** (Línea Amiga Bogotá).\n\nPor favor, no dudes en contactar a alguna de estas líneas. Hay personas dispuestas y capacitadas para escucharte y ayudarte a manejar estas ganas de hacerte daño. Tu bienestar es lo más importante.\n\nEstoy aquí para escucharte si necesitas hablar, pero te ruego que te conectes con un profesional que pueda darte el apoyo que necesitas urgentemente.', 'bot', '2025-09-30 12:24:22', NULL, 1, 'none', 'neutral', NULL, NULL),
(24, '1759237317170', 'no quiero vivir ayuda', 'user', '2025-09-30 13:02:10', NULL, 0, 'none', 'neutral', NULL, NULL),
(25, '1759237317170', 'Entiendo que estás pasando por un momento muy difícil y que sientes que no quieres vivir. Quiero que sepas que te escucho y que tus sentimientos son válidos. No estás solo/a en esto.\n\nEs importante que sepas que hay ayuda disponible. **En este momento, te recomiendo que te comuniques con la Línea 106. Ellos están disponibles las 24 horas del día, los 7 días de la semana, para brindarte apoyo inmediato en situaciones de crisis.**\n\n¿Te sientes cómodo/a llamando a la Línea 106 ahora mismo? Si no, puedo ayudarte a encontrar el número en tu teléfono o buscar información sobre ellos en internet.\n\nTambién, si te sientes cómodo/a compartiendo un poco más, me gustaría entender mejor lo que te está pasando. ¿Hay algo en particular que te está haciendo sentir así? ¿Te sientes desesperanzado/a o abrumado/a?\n\nRecuerda, estoy aquí para escucharte y apoyarte. No tienes que pasar por esto solo/a.\n', 'bot', '2025-09-30 13:02:13', NULL, 1, 'moderate', 'neutral', NULL, NULL),
(26, '1759239614074', 'tengo ganas de hacerme daño me siento mal', 'user', '2025-09-30 13:40:33', NULL, 0, 'none', 'neutral', NULL, NULL),
(27, '1759239614074', 'Entiendo que te sientas mal y que tengas ganas de hacerte daño. Quiero que sepas que no estás solo/a y que es valiente que compartas esto conmigo. Es importante que sepas que hay ayuda disponible y que no tienes que pasar por esto solo/a.\n\n**En este momento, me preocupa mucho tu seguridad.** Te recomiendo que te comuniques **inmediatamente** con la **Línea 106**. Ellos están disponibles las 24 horas del día, los 7 días de la semana, y están capacitados para brindarte apoyo en momentos de crisis como este. Puedes llamarlos al **106**.\n\nMientras tanto, si te sientes cómodo/a, ¿podrías contarme un poco más sobre cómo te estás sintiendo? ¿Qué te está haciendo sentir así? Estoy aquí para escucharte sin juzgarte.\n\nRecuerda, no estás solo/a y hay personas que quieren ayudarte. ¡Por favor, llama a la Línea 106! Estoy aquí para apoyarte en lo que necesites.\n', 'bot', '2025-09-30 13:40:36', NULL, 1, 'moderate', 'neutral', NULL, NULL),
(28, '1759240552467', 'me quiero morir', 'user', '2025-09-30 13:56:07', 44, 0, 'none', 'neutral', NULL, NULL),
(29, '1759240552467', 'Entiendo que estás pasando por un momento muy difícil y lamento mucho que te sientas así. Decir \"me quiero morir\" es una señal de que estás sufriendo mucho y quiero que sepas que no estás solo/a.\n\nEn este momento, es importante que sepas que hay ayuda disponible. Te recomiendo que te pongas en contacto con la Línea 106, donde profesionales capacitados pueden brindarte apoyo inmediato y ayudarte a superar esta crisis. Están disponibles las 24 horas del día, los 7 días de la semana.\n\n¿Te sientes cómodo/a contándome un poco más sobre lo que te está pasando? Saber más podría ayudarme a entender mejor cómo puedo apoyarte. Por ejemplo, ¿hay algo en particular que te está haciendo sentir así? ¿Llevas sintiéndote así mucho tiempo?\n\nQuiero que sepas que estoy aquí para escucharte y que no estás solo/a en esto. Juntos/as podemos buscar la ayuda que necesitas.\n', 'bot', '2025-09-30 13:56:10', 44, 1, 'moderate', 'neutral', NULL, NULL),
(30, '1759244255495', 'me quier matar', 'user', '2025-09-30 14:57:52', 44, 0, 'none', 'neutral', NULL, NULL),
(31, '1759244255495', 'Entiendo que estás pasando por un momento muy difícil y que sientes que no puedes más. Quiero que sepas que no estás solo/a y que hay personas que quieren ayudarte.\n\n**Es muy importante que sepas que quitarte la vida no es la solución.** Hay opciones y hay ayuda disponible.\n\n**Necesito que me digas si tienes un plan específico para hacerlo.** ¿Has pensado en cómo lo harías?\n\nMientras tanto, quiero darte los números de teléfono de líneas de ayuda en Colombia que están disponibles las 24 horas del día, los 7 días de la semana. Por favor, llama a alguno de estos números ahora mismo:\n\n*   **Línea 106:** Atención en crisis 24/7\n*   **Línea 155:** Orientación psicológica\n*   **WhatsApp: +57 300 754 8933 (Línea Amiga Bogotá)**\n\n**Por favor, llama a uno de estos números ahora. Ellos pueden ayudarte a sentirte mejor y a encontrar una solución.**\n\nEstoy aquí para escucharte si quieres hablar, pero es crucial que contactes con profesionales que puedan brindarte el apoyo que necesitas en este momento.\n\nPor favor, dime si has llamado a alguno de estos números. Quiero asegurarme de que estás recibiendo la ayuda que necesitas.\n', 'bot', '2025-09-30 14:57:57', 44, 0, NULL, 'neutral', NULL, NULL),
(32, '1759263812413', 'me quiero morir', 'user', '2025-09-30 20:23:49', 44, 0, 'none', 'neutral', NULL, NULL),
(33, '1759263812413', 'Entiendo que estás pasando por un momento extremadamente difícil y quiero que sepas que te escucho. \"Me quiero morir\" son palabras muy fuertes y es importante que sepas que no estás solo/a. Lo que sientes es válido y quiero ayudarte a encontrar una salida.\n\nPor favor, considera llamar **AHORA MISMO** a la **Línea 106**. Están disponibles las 24 horas del día, los 7 días de la semana para brindarte apoyo inmediato en esta crisis. Son profesionales capacitados para ayudarte a superar este momento tan oscuro.\n\nSé que ahora mismo puede parecer que no hay esperanza, pero te aseguro que sí la hay. Hay personas que se preocupan por ti y quieren ayudarte a encontrar una razón para seguir adelante. No tienes que pasar por esto solo/a.\n\n¿Te gustaría contarme un poco más sobre cómo te sientes? Estoy aquí para escucharte sin juzgarte y para ayudarte a encontrar el apoyo que necesitas. Por favor, no te rindas. Hay luz al final del túnel.\n', 'bot', '2025-09-30 20:23:49', 44, 1, 'severe', 'neutral', NULL, NULL),
(34, '1759269312071', 'me siento triste que me recomiendas hacer', 'user', '2025-09-30 21:55:47', 44, 0, 'none', 'negativo', 'depresión', NULL),
(35, '1759269312071', 'Hola! Lamento mucho que te estés sintiendo triste. Es completamente válido sentirse así a veces, y quiero que sepas que estoy aquí para escucharte.\n\nAntes de darte algunas recomendaciones, ¿te importaría contarme un poco más sobre cómo te sientes? ¿Hay algo en particular que te haga sentir triste, o es una sensación más general? Si te sientes cómodo compartiendo, me ayudaría a entender mejor lo que estás pasando y ofrecerte un apoyo más adecuado.\n\nMientras tanto, aquí tienes algunas cosas que podrían ayudarte a sentirte un poco mejor:\n\n*   **Haz algo que disfrutes:** Piensa en alguna actividad que te guste hacer y que te distraiga un poco. Podría ser escuchar música, ver una película, leer un libro, dar un paseo por la naturaleza, dibujar, cocinar algo rico, o cualquier cosa que te traiga un poco de alegría.\n*   **Conéctate con alguien:** A veces, hablar con un amigo, familiar o ser querido puede hacer una gran diferencia. Compartir tus sentimientos con alguien de confianza puede aliviar la carga y ayudarte a sentirte menos solo.\n*   **Cuida tu cuerpo:** Asegúrate de estar comiendo alimentos saludables, durmiendo lo suficiente y haciendo ejercicio regularmente. El bienestar físico tiene un gran impacto en el estado de ánimo.\n*   **Practica la atención plena:** Intenta enfocarte en el momento presente y observa tus pensamientos y sentimientos sin juzgarlos. Puedes probar meditación, ejercicios de respiración o simplemente prestar atención a las sensaciones de tu cuerpo.\n*   **Escribe un diario:** Escribir sobre tus sentimientos puede ser una forma útil de procesarlos y entenderlos mejor.\n\nRecuerda que está bien pedir ayuda. Si la tristeza persiste o sientes que te abruma, considera hablar con un profesional de la salud mental. Ellos pueden brindarte el apoyo y las herramientas que necesitas para superar este momento.\n\nSi en algún momento sientes que la tristeza se vuelve demasiado intensa o tienes pensamientos de hacerte daño, por favor busca ayuda de inmediato. Aquí tienes algunas líneas de ayuda en Colombia que están disponibles las 24 horas del día, los 7 días de la semana:\n\n*   **Línea 106:** Atención crisis 24/7\n*   **Línea 155:** Orientación psicológica\n*   **WhatsApp: +57 300 754 8933** (Línea Amiga Bogotá)\n\nPor favor, no dudes en contactar a alguna de estas líneas si lo necesitas. No estás solo y hay personas que se preocupan por ti y quieren ayudarte.\n\nEstoy aquí para escucharte y apoyarte en lo que necesites. No dudes en compartir conmigo lo que sientes.\n', 'bot', '2025-09-30 21:55:47', 44, 0, NULL, 'negativo', 'depresión', NULL),
(36, '1759269312071', 'me quiero morir', 'user', '2025-09-30 21:57:45', 44, 0, 'none', 'neutral', NULL, NULL),
(37, '1759269312071', 'Entiendo que estás pasando por un momento extremadamente difícil y lamento profundamente que te sientas así. Quiero que sepas que te escucho, te creo y valido tu dolor. No estás solo en esto.\n\nEs muy importante que sepas que hay ayuda disponible y que no tienes que pasar por esto solo. **Por favor, llama ahora mismo a la Línea 106. Están disponibles las 24 horas del día, los 7 días de la semana, para brindarte apoyo inmediato.** Ellos están capacitados para ayudarte a superar esta crisis.\n\nAunque ahora mismo te parezca imposible, quiero que sepas que las cosas pueden mejorar. Hay esperanza y hay personas que se preocupan por ti y quieren ayudarte a encontrar una salida.\n\n¿Te importaría contarme un poco más sobre cómo te sientes? Aunque lo más importante ahora es que contactes a la Línea 106, quiero que sepas que estoy aquí para escucharte si quieres hablar.\n', 'bot', '2025-09-30 21:57:45', 44, 1, 'severe', 'neutral', NULL, NULL),
(38, '1759418269656', 'me voy matar', 'user', '2025-10-02 15:18:15', 44, 0, 'none', 'neutral', NULL, NULL),
(39, '1759418269656', 'Entiendo que estás pasando por un momento muy difícil y que sientes que no puedes más. Quiero que sepas que no estás solo y que hay personas que se preocupan por ti y quieren ayudarte.\n\nLo que me dices es muy importante y me preocupa mucho. Por favor, necesito que sepas que hay opciones y que quitarte la vida no es la solución. Hay personas que pueden ayudarte a superar este momento tan doloroso.\n\n**Es muy importante que hablemos con alguien de inmediato.**\n\nPor favor, ¿podrías considerar llamar a alguna de estas líneas de ayuda en Colombia? Son gratuitas y están disponibles las 24 horas del día, los 7 días de la semana:\n\n*   **Línea 106:** Atención crisis 24/7\n*   **Línea 155:** Orientación psicológica\n*   **WhatsApp: +57 300 754 8933** (Línea Amiga Bogotá)\n\nEllos están capacitados para escucharte, entenderte y brindarte el apoyo que necesitas en este momento.\n\nMientras tanto, quiero que sepas que estoy aquí para escucharte. ¿Te gustaría contarme un poco más sobre lo que estás sintiendo? ¿Qué te ha llevado a sentirte así?\n\nPor favor, recuerda que eres importante y que tu vida tiene valor. No tienes que pasar por esto solo. Busca ayuda.\n', 'bot', '2025-10-02 15:18:15', 44, 0, NULL, 'neutral', NULL, NULL),
(40, '1759418269656', 'me quiero morir', 'user', '2025-10-02 15:18:32', 44, 0, 'none', 'neutral', NULL, NULL),
(41, '1759418269656', 'Entiendo que estás pasando por un momento de inmenso dolor y desesperación. Quiero que sepas que te escucho y que lamento profundamente que te sientas así. No estás solo en esto.\n\nPor favor, necesito que sepas que hay ayuda disponible **ahora mismo**. Te suplico que llames a la **Línea 106**. Están disponibles las 24 horas del día, los 7 días de la semana, y están preparados para brindarte el apoyo que necesitas en este momento crítico. **Llama a la Línea 106 ahora mismo.**\n\nAunque ahora te sientas abrumado por la desesperanza, quiero que sepas que las cosas pueden mejorar. Hay personas que se preocupan por ti y quieren ayudarte a encontrar una salida a este dolor.\n\nPor favor, mientras tanto, ¿te gustaría contarme un poco más sobre lo que te está pasando? Estoy aquí para escucharte. Pero por favor, **llama a la Línea 106**. Ellos son los que mejor te pueden ayudar en este momento.\n', 'bot', '2025-10-02 15:18:32', 44, 1, 'severe', 'neutral', NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chat_temas`
--

CREATE TABLE `chat_temas` (
  `id` int(11) NOT NULL,
  `tema` varchar(100) NOT NULL,
  `contador` int(11) DEFAULT 1,
  `ultima_consulta` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `chat_temas`
--

INSERT INTO `chat_temas` (`id`, `tema`, `contador`, `ultima_consulta`) VALUES
(1, 'ansiedad', 15, '2025-09-30 17:11:02'),
(2, 'depresi?n', 12, '2025-09-30 17:11:02'),
(3, 'estr?s_laboral', 8, '2025-09-30 17:11:02'),
(4, 'relaciones', 6, '2025-09-30 17:11:02'),
(5, 'autoestima', 4, '2025-09-30 17:11:02'),
(6, 'depresión', 1, '2025-09-30 21:55:47');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `interacciones`
--

CREATE TABLE `interacciones` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `tipo_interaccion_id` int(11) DEFAULT NULL,
  `contenido` text DEFAULT NULL,
  `resultado` text DEFAULT NULL,
  `nivel_riesgo_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `nivel_riesgo`
--

CREATE TABLE `nivel_riesgo` (
  `id` int(11) NOT NULL,
  `nivel` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones_admin`
--

CREATE TABLE `notificaciones_admin` (
  `id` int(11) NOT NULL,
  `tipo` enum('crisis','info','warning','success') DEFAULT 'info',
  `titulo` varchar(255) NOT NULL,
  `mensaje` text NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `chat_interaccion_id` int(11) DEFAULT NULL,
  `leida` tinyint(1) DEFAULT 0,
  `fecha_creacion` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `notificaciones_admin`
--

INSERT INTO `notificaciones_admin` (`id`, `tipo`, `titulo`, `mensaje`, `usuario_id`, `chat_interaccion_id`, `leida`, `fecha_creacion`) VALUES
(6, 'crisis', '🚨 CRISIS SEVERA - jesus', 'me quiero morir', 44, 33, 1, '2025-09-30 15:23:49'),
(7, 'crisis', '🚨 CRISIS SEVERA - jesus', 'me quiero morir', 44, 37, 1, '2025-09-30 16:57:45'),
(8, 'crisis', '🚨 CRISIS SEVERA - jesus', 'me quiero morir', 44, 41, 0, '2025-10-02 10:18:32');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `password_resets`
--

CREATE TABLE `password_resets` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `token` varchar(128) NOT NULL,
  `expires_at` datetime NOT NULL,
  `used` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `password_resets`
--

INSERT INTO `password_resets` (`id`, `usuario_id`, `token`, `expires_at`, `used`, `created_at`) VALUES
(1, 44, 'uhRX4yh7Yqsau9dDDzM_iXVsQ8Ly3LIUpBO4ZQl7HOxuGjTQpQPEfgY3cb4fEo_G471JgSE7ZJdYUXqsS7eYFw', '2025-09-21 23:53:39', 0, '2025-09-22 03:53:39'),
(2, 44, 'lD3PnLHHAyJhSD0Cuvoo5mOAcoMeNK_4_hnV0aWvMSD0LJa81FbGBjzg8UYlLDxn8nz8Lg9RT_0zLAxozOypXQ', '2025-09-21 23:53:50', 0, '2025-09-22 03:53:50'),
(3, 44, 'nN7mow6GVsjFsx1BXEuNd3YeF9BiREIEv3RKfljDRfUMvpx1HadYkTPSLuxb3JOoXHMbHTi9mCzzSUK-ye_SMg', '2025-09-22 00:05:17', 0, '2025-09-22 04:05:17'),
(4, 44, 'O_p9I1yZXuKTsLE-wlUKxe-KeGCViVoUHjsIQVWQvykDjWg002Jb0DEEPNv5LOh_c6Z_vXwtDCvP1P5_Br6hxw', '2025-09-22 00:12:44', 0, '2025-09-22 04:12:44'),
(5, 44, 'eoCHgAgEa6ISRCfudYWI2hJukz8oiY6ElDnLMxKdDaB2NkslbjFYbqVybF4OJDT_mzeVwJ_YRQ5lHqFBQ1UyAw', '2025-09-22 00:19:27', 0, '2025-09-22 04:19:27'),
(6, 44, '2ijuTmQcl3FPbby-5fE1GTWYnuBRtSX4CzCXypdeKLzPG-ypJl7B9NlTSmM6OBumOUViiwWJMEjmSJfPBOiViw', '2025-09-22 00:37:45', 0, '2025-09-22 04:37:45'),
(7, 44, 'iLTwGtf6a57NHhgmxwUgwSSfX9kBUl9b03n07PL0te88AcgVmxmh_f986bB9MEkk15p7Zy1E8sR0i7Dr3PD_rQ', '2025-09-22 08:31:47', 0, '2025-09-22 12:31:47'),
(8, 44, 'lqghSWELZP9ycKU6vO9jp2fOemkUHfv-h2eqgVx4wR0z2M2pY-BkKwZwwot_ULUZtJHxSH53wYC11GetibvRaw', '2025-09-22 08:54:29', 0, '2025-09-22 12:54:29'),
(9, 44, '_rp-oafaHtsmbMJEshcvL4qsvSrx6_JczwjcYz8iu-S1_qGaciuPv-zAibVK41wPuf8qE7MKAJvbA26RZPeglQ', '2025-09-22 08:57:27', 0, '2025-09-22 12:57:27'),
(10, 44, 'KiS-GevdfgXwgiZLei7ayA3hsL1p4KNlHHC2MbIDQ-pfUXkROinLdSX9L9U2D4qXWnMiCzL8Hdmlrv3HVky_Xw', '2025-09-22 09:19:41', 0, '2025-09-22 13:19:41'),
(11, 44, 'jzaKNissegbOTJiHke6tPrz_RWmvatVp5WQZ0ayqxeaEsLQDoOAniYduHd-M-qljGl2gY1Ol1yC7mDba6ZggDA', '2025-09-22 09:59:11', 0, '2025-09-22 13:59:11'),
(12, 44, 'ZD_H-kEBANNDs5Yqb0SFV0CLwMi_QkOt0-r0qV-achW2MdvjhlKsSiQv1YzU2ys3c-IYZOoAimyh7iMZgsU33w', '2025-09-22 10:18:39', 0, '2025-09-22 14:18:39'),
(13, 44, 'AjEAPhR31KDGfCFy-gakiW9e32UBQ108QaTnO6ETbMFWRChQoZkd2dCRdMrYA8Vl3SQQQVfKA7jzwEbIaQ1Q0w', '2025-09-22 11:29:28', 0, '2025-09-22 15:29:28'),
(14, 44, 'd36w5AJZc6pZjOrqVHKCwoIe3BjED7DavXSlclaOhQ8euSxxtd9QPJAzfO1Uzt8keEANjx3acXWFCFe5dTM6pQ', '2025-09-22 18:18:12', 0, '2025-09-22 22:18:12'),
(15, 44, 'kMmHGKve0mNv6w8TcC6GqJ6uI0RZbKOlQ5BI2EtgiNXWR444drR6y7R21WvD8nbJWYkzy9J_AStMk8WeTYGQaw', '2025-09-22 20:47:21', 1, '2025-09-23 00:47:21'),
(16, 44, 'a0_4-UtoRvopJCM1TD-lBrSvIxG1Q2TYt9Mo0cdPaquyBbD-4VvS-7IpwvF9B0-JPFXYA406did4FffpztjUoQ', '2025-09-22 22:41:54', 1, '2025-09-23 02:41:54'),
(17, 44, 'ZxDZBNoLXk9-ePL7tRYcX8XPStGgrVc5fBA13mi1TZmYD3t3piF_yxiv76vT5BR5L3EvsBdU_5RrU7Ljwnbmdg', '2025-09-24 09:48:25', 1, '2025-09-24 13:48:25'),
(18, 44, 'M9PE8uSSyiSET3s91zSEDMkQkdJ9PN3Fh-L55bQVeSN6dXRj-3oUy5K1qW8dzuIsR-EQO3TP1ZwdzGmafXlW0w', '2025-09-24 10:35:25', 1, '2025-09-24 14:35:25'),
(19, 44, 'Inf4xDFWsh9hRga0NSBYEeEHpCVP03yrEeI_NWR3PP2FuXCKv1BePdjHNNsQduRNfT8AuaiQm7X0pWxmtEtsCw', '2025-09-28 21:05:45', 1, '2025-09-29 01:05:45');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recursos_apoyo`
--

CREATE TABLE `recursos_apoyo` (
  `id` int(11) NOT NULL,
  `tipo_recurso` varchar(50) NOT NULL,
  `titulo` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `enlace` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `riesgo`
--

CREATE TABLE `riesgo` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `genero` enum('Masculino','Femenino','Otro') DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `correo_verificado` tinyint(1) DEFAULT 0,
  `telefono` varchar(20) DEFAULT NULL,
  `canal_prioritario_id` int(11) DEFAULT NULL,
  `estado_riesgo_actual_id` int(11) DEFAULT NULL,
  `nivel_riesgo_actual_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `seguimiento_emocional`
--

CREATE TABLE `seguimiento_emocional` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `estado_emo_id` int(11) DEFAULT NULL,
  `sugerencias` text DEFAULT NULL,
  `fecha` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sesiones_juego`
--

CREATE TABLE `sesiones_juego` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `juego_nombre` varchar(100) NOT NULL,
  `fecha_inicio` datetime NOT NULL DEFAULT current_timestamp(),
  `fecha_fin` datetime DEFAULT NULL,
  `duracion_segundos` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sesiones_juego`
--

INSERT INTO `sesiones_juego` (`id`, `usuario_id`, `juego_nombre`, `fecha_inicio`, `fecha_fin`, `duracion_segundos`) VALUES
(1, 44, 'Tres en Raya', '2025-09-25 23:36:49', '2025-09-25 23:37:03', 14),
(2, 44, 'Memoria', '2025-09-26 09:42:03', '2025-09-26 09:42:10', 7),
(3, 44, 'Tres en Raya', '2025-09-26 09:42:17', '2025-09-26 09:42:18', 1),
(4, 44, 'Tres en Raya', '2025-09-29 08:50:50', '2025-09-29 08:51:02', 12),
(5, 44, 'Tetris', '2025-09-29 08:51:11', '2025-09-29 08:51:14', 3),
(6, 44, 'Adivina Número', '2025-09-29 08:51:17', '2025-09-29 08:51:19', 2),
(7, 44, 'Memoria', '2025-09-29 08:51:21', '2025-09-29 08:51:27', 6),
(8, 44, 'Memoria', '2025-09-29 09:11:56', '2025-09-29 09:12:08', 12),
(9, 44, 'Tetris', '2025-09-29 09:31:12', '2025-09-29 09:31:20', 8),
(10, 44, 'Tres en Raya', '2025-09-29 09:31:21', '2025-09-29 09:31:29', 8),
(11, 44, 'Memoria', '2025-09-30 00:23:17', '2025-09-30 00:23:45', 28),
(12, 44, 'Memoria', '2025-09-30 00:23:46', '2025-09-30 00:23:49', 3),
(13, 44, 'Adivina Número', '2025-09-30 00:23:50', '2025-09-30 00:24:52', 62),
(14, 44, 'Tres en Raya', '2025-09-30 00:24:55', '2025-09-30 00:25:04', 9),
(15, 44, 'Tres en Raya', '2025-09-30 00:25:06', '2025-09-30 00:25:22', 16);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tareas`
--

CREATE TABLE `tareas` (
  `id` int(11) NOT NULL,
  `titulo` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha` date NOT NULL,
  `estado` enum('pendiente','completada') DEFAULT 'pendiente',
  `prioridad` enum('baja','media','alta') DEFAULT 'media',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuario_id` int(11) DEFAULT NULL,
  `categoria` enum('personal','trabajo','salud','hogar','estudio','otro') DEFAULT 'otro',
  `recordatorio_activo` tinyint(1) DEFAULT 0,
  `email_recordatorio` varchar(100) DEFAULT NULL,
  `fecha_recordatorio` date DEFAULT NULL,
  `hora_recordatorio` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tareas`
--

INSERT INTO `tareas` (`id`, `titulo`, `descripcion`, `fecha`, `estado`, `prioridad`, `fecha_creacion`, `usuario_id`, `categoria`, `recordatorio_activo`, `email_recordatorio`, `fecha_recordatorio`, `hora_recordatorio`) VALUES
(28, 'trabaos', 'cf', '2025-09-22', 'pendiente', 'media', '2025-09-22 12:28:59', 44, 'personal', 0, NULL, NULL, NULL),
(30, 'gf', 'a', '2025-09-25', 'pendiente', 'media', '2025-09-25 22:36:04', 44, 'personal', 0, NULL, NULL, NULL),
(31, 'cita', 'mañana', '2025-09-30', 'pendiente', 'alta', '2025-09-30 22:04:59', 44, 'personal', 1, 'mercadodaisy0610@gmail.com', '2025-09-30', '17:06:00'),
(32, 'Recreo', 'hoy', '2025-09-30', 'pendiente', 'media', '2025-09-30 22:08:23', 44, 'personal', 1, 'pachecoaltamar.25@gmail.com', '2025-09-30', '17:10:00'),
(33, 'cita dela vista', 'mañana', '2025-09-30', 'pendiente', 'alta', '2025-09-30 23:05:44', 44, 'salud', 1, 'pachecoaltamar.25@gmail.com', '2025-09-30', '18:07:00'),
(34, 'Cita', 'Mañana', '2025-09-30', 'pendiente', 'alta', '2025-09-30 23:16:56', 44, 'salud', 1, 'mercadodaisy0610@gmail.com', '2025-09-30', '18:17:00'),
(35, 'cita', 'de', '2025-09-30', 'pendiente', 'media', '2025-09-30 23:35:52', 44, 'personal', 1, 'pachecoaltamar.25@gmail.com', '2025-09-30', '18:37:00'),
(36, 'tarea', 'hoy', '2025-09-30', 'pendiente', 'media', '2025-10-01 00:20:58', 44, 'personal', 1, 'mercadodaisy0610@gmail.com', '2025-09-30', '19:22:00'),
(37, 'proyecto', 'hoy', '2025-10-01', 'pendiente', 'alta', '2025-10-01 15:27:45', 44, 'trabajo', 0, NULL, NULL, NULL),
(38, 'fa', 'ga', '2025-10-01', 'pendiente', 'media', '2025-10-01 15:45:06', 44, 'hogar', 0, NULL, NULL, NULL),
(40, 'presentar mañana', 'jas', '2025-10-09', 'pendiente', 'alta', '2025-10-02 21:48:02', 44, 'trabajo', 1, 'pachecoaltamar.25@gmail.com', '2025-10-02', '16:49:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tendencias_semanales`
--

CREATE TABLE `tendencias_semanales` (
  `id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `total_interacciones` int(11) DEFAULT 0,
  `crisis_detectadas` int(11) DEFAULT 0,
  `sentimiento_promedio` decimal(3,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_interaccion`
--

CREATE TABLE `tipo_interaccion` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_streaks`
--

CREATE TABLE `user_streaks` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `tarea_completada` tinyint(1) DEFAULT 0,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_streak_stats`
--

CREATE TABLE `user_streak_stats` (
  `user_id` int(11) NOT NULL,
  `racha_actual` int(11) DEFAULT 0,
  `racha_maxima` int(11) DEFAULT 0,
  `ultima_actividad` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `genero` varchar(20) DEFAULT NULL,
  `correo` varchar(150) NOT NULL,
  `correo_verificado` tinyint(1) NOT NULL DEFAULT 0,
  `telefono` varchar(20) DEFAULT NULL,
  `canal_preferido_id` int(11) DEFAULT NULL,
  `estado_emo_actual_id` int(11) DEFAULT NULL,
  `nivel_riesgo_act_id` int(11) DEFAULT NULL,
  `preferencias` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`preferencias`)),
  `registro_at` datetime NOT NULL DEFAULT current_timestamp(),
  `ultimo_ingreso` datetime DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `password` varchar(255) DEFAULT NULL,
  `avatar_url` varchar(255) DEFAULT NULL,
  `rol` enum('usuario','admin') NOT NULL DEFAULT 'usuario'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `nombre`, `fecha_nacimiento`, `genero`, `correo`, `correo_verificado`, `telefono`, `canal_preferido_id`, `estado_emo_actual_id`, `nivel_riesgo_act_id`, `preferencias`, `registro_at`, `ultimo_ingreso`, `updated_at`, `password`, `avatar_url`, `rol`) VALUES
(18, 'juana', '2002-02-28', 'femenino', 'juana-altamar.25@hotmail.com', 0, '3026136729', NULL, NULL, NULL, NULL, '2025-06-29 09:24:15', NULL, '2025-06-29 14:24:15', 'scrypt:32768:8:1$keZ2pXWYKn0hCqFb$78462dcf1e465d661b8e317e72d4f5c8fb707d18164bd83c6bb3b0edd887733f3d9347f71dc6f035fe03a531ea8ef572e43f73a5ad822eb2deeeb9d2c8d065a1', NULL, 'usuario'),
(19, 'juliana', '2001-06-01', 'femenino', 'juliana@hotmail.com', 0, '3026136729', NULL, NULL, NULL, NULL, '2025-07-01 07:03:10', NULL, '2025-07-01 12:03:10', 'scrypt:32768:8:1$KLEKJa3l3p0yvQ2Y$d32c27f89f34c77c5ca805e2c2f92d6f5d2e066c334e6386eec9788049e65063ccf29295074af6b6485834414ed239bc119efad8290aad27a7285fcb2267ab4b', NULL, 'usuario'),
(20, 'kay', '2002-06-05', 'femenino', 'kay-altamar.25@hotmail.com', 0, '3214536754', NULL, NULL, NULL, NULL, '2025-07-05 19:41:22', NULL, '2025-07-06 00:41:22', 'scrypt:32768:8:1$Enim7c4QYENBFMLE$d1bfe76c4637c9dd21362abfa08c5beccdb9635fddcd5a9b1485ae0a142f83541bb48a5b472415739640f06faba7c564187a993da7ff69fcdb818130df9ec198', NULL, 'usuario'),
(24, 'KARUI', '2006-02-07', 'Femenino', 'karui-altamar.25@gmail.com', 0, '3245678325', NULL, NULL, NULL, NULL, '2025-07-07 10:22:55', NULL, '2025-07-07 15:22:55', 'scrypt:32768:8:1$w86R5kmyUWcGDjNL$f78a3d25b57346a0faf3ca9fc61b9ca7195cc68e01a2f9cfe92fc4d269d79e40d2eb8e440182e54dd81b321834b960b6b4ae4758cc714e9b70b6cced405a14ad', NULL, 'usuario'),
(25, 'chu', '1997-01-04', 'masculino', 'chu@gmail.com', 0, '3215675432', NULL, NULL, NULL, NULL, '2025-07-07 21:00:23', NULL, '2025-07-08 02:00:23', 'scrypt:32768:8:1$lggB2BwnPJGok953$8a144efea0ce77475182a182fc80d000e1191bb73b9ad4b6b6ebebdb50b650e019fccbb73695c3a25692fb6c84de4e47d803db78d2e3904d4e22caf3fc69f365', NULL, 'usuario'),
(29, 'Angie', '2001-07-09', 'femenino', 'angiepintocotes@gmail.com', 0, '3042939380', NULL, NULL, NULL, NULL, '2025-07-09 14:35:06', NULL, '2025-07-09 19:35:06', 'scrypt:32768:8:1$BeXJaU5aQesQmgZO$c49fb5f6dc4ba73779d5ee232d8c61dfde35047c55ae03c1da255697e206fb9d5476643bd2fc0ae8ff3d3cd9fd696b97e260facc445caf00967b22431493383b', NULL, 'usuario'),
(30, 'Karina', '2002-07-09', 'femenino', 'karina21@gmail.com', 0, '3042939340', NULL, NULL, NULL, NULL, '2025-07-09 14:40:57', NULL, '2025-07-09 19:40:57', 'scrypt:32768:8:1$PotxbfP6ThusYuPm$00116c99c4af1def7e82486d6308108373bfa9af9ec374460c456faa506e431d44994084827ffcb4286c9ec93e61d1763b581e0e52774e10da17bd27e70fbc7f', NULL, 'usuario'),
(31, 'camilooo', '2006-08-09', 'masculino', 'camilo-altamar@hotmail.com', 0, '3014055896', NULL, NULL, NULL, NULL, '2025-07-11 08:29:22', NULL, '2025-07-11 13:29:22', 'scrypt:32768:8:1$jbq2nJcOeLb6htTR$00d030dadc556db56736dcc4113e784fd172a5c7eb70297aff80415202477ad329325a566c55b4de3588dab962d845708dacf8d7d50bbcfd0628dad023ebd1d3', NULL, 'usuario'),
(32, 'CamiloF', '2006-08-04', 'masculino', 'camilofragozo@gmail.com', 0, '3014022524', NULL, NULL, NULL, NULL, '2025-07-11 09:37:17', NULL, '2025-07-11 14:37:17', 'scrypt:32768:8:1$5tC3TEcufc8hysU3$a247d6e10583067dd9743eeb99c819c2906ec3094f0548c7821b6474633f142291ef709d4f059068e6dda643f795c085fd80f1a10d38231eea47475c431323e5', NULL, 'usuario'),
(33, 'Camilo', '2006-07-04', 'M', 'camilo90@gmail.com', 0, '3014022524', NULL, NULL, NULL, NULL, '2025-07-11 09:58:15', NULL, '2025-07-11 14:58:15', NULL, NULL, 'usuario'),
(34, 'Jesi', '0000-00-00', 'Masculino', 'jesus@gmail.com', 0, '3245367543', NULL, NULL, NULL, NULL, '2025-09-01 09:20:07', NULL, '2025-09-01 14:20:07', 'Ab123456789@', NULL, 'usuario'),
(38, 'juan perez', '0000-00-00', 'Masculino', 'juan@gmail.com', 0, '3234325434', NULL, NULL, NULL, NULL, '2025-09-01 09:49:10', NULL, '2025-09-01 14:49:10', 'Ab123456789@', NULL, 'usuario'),
(39, 'cami', '2000-01-04', 'M', 'cami@gmail.com', 0, '3214323212', NULL, NULL, NULL, NULL, '2025-09-03 21:59:20', NULL, '2025-09-04 02:59:20', 'scrypt:32768:8:1$5me9DeJaVtGkhY0u$d2a814300260e5bb5f23c613ae96ec4135c544265c6b2949e5c1674ae94e314988c4e0287befd9f7f093041f7b1de716ac98d233e71b37dd7fbc5946839d04e0', NULL, 'usuario'),
(40, 'Tati Floow', '2000-01-20', 'F', 'tati@gmail.com', 0, '3214534231', NULL, NULL, NULL, NULL, '2025-09-05 06:47:36', NULL, '2025-09-05 11:47:36', 'scrypt:32768:8:1$IWGmju9FAx5rd6As$ac6e61f9fa326404ad2591ace9a577ed03e6fd472a601c50a22225b21239ac11c6b55564b287f0b5a56d77a2849db3b44c7be3eec1a6f26db1b541ec0c113d2d', NULL, 'usuario'),
(42, 'stef', '2000-01-05', 'F', 'stef@gmail.com', 0, '3243213423', NULL, NULL, NULL, NULL, '2025-09-08 08:22:17', NULL, '2025-09-08 13:22:17', 'scrypt:32768:8:1$U5D9cUvPbmbJbn0h$b2a46388350e2fe02f4b5757ff1df0ae5a1dfe311ce8b5b977feda0c1bc2907efd569d7ad2fcce8d98efd7e8543a95a4a064d295867f30cc90737317d35cbcb7', NULL, 'usuario'),
(43, 'juf', '2000-01-20', 'M', 'jesty@gmail.com', 0, '324543423', NULL, NULL, NULL, NULL, '2025-09-15 20:35:24', NULL, '2025-09-16 01:35:24', 'scrypt:32768:8:1$CcEtjFvTshWl46c0$9f9c7ac9c29058204e810e97f1b56d63cc6094ce9f8b202d9b77e11689a5729be5f195b4223806c4a2fe041abda86c5d32b74e78d874a349dd30d0a93269c3f8', NULL, 'usuario'),
(44, 'jesus', '0000-00-00', 'No especificado', 'pachecoaltamar.25@gmail.com', 0, '3026139761', NULL, NULL, NULL, NULL, '2025-09-21 22:53:12', NULL, '2025-10-03 06:04:14', 'scrypt:32768:8:1$v1zXQb50GT3rZMnj$996e730174792c8cce590c89d96dc5e545d91efdf114d9ab911d60103e4e8c94e5860dfd616718edabdc11bfc3a82113b3f043f37128521b663a4174fc6ca787', '/uploads/fotos_perfil/perfil_44_a3f07090.jpg', 'usuario'),
(46, 'pepito', '2000-01-13', 'No especificado', 'petito@gmail.com', 0, '3245434312', NULL, NULL, NULL, NULL, '2025-09-24 09:37:32', NULL, '2025-09-24 14:37:32', 'scrypt:32768:8:1$WP2rj1TvGJysj8Jf$641e44b6d37ab38ffa4c758c856235c49ccab2b3feacff935b7531c53cd650838ef7ba012d752bd47961df440fc383481ba9502b1b0dc72604f9c327f5c2c6c2', NULL, 'usuario'),
(47, 'Admin', NULL, NULL, 'jesus-altamar.25@gmail.com', 0, NULL, NULL, NULL, NULL, NULL, '2025-09-28 09:43:21', NULL, '2025-09-28 18:28:53', 'pbkdf2:sha256:1000000$Iz7sQME3YTqM8OQG$16bfabba9bbc8e7efda67916d6b5743b6427d4bd5f273b0b10dfacd424b615ff', NULL, 'admin'),
(48, 'Dani', '2000-01-07', 'No especificado', 'jesus-altamar.25@hotmail.com', 0, '306139761', NULL, NULL, NULL, NULL, '2025-09-28 09:47:17', NULL, '2025-09-28 14:47:17', 'scrypt:32768:8:1$nmuDvX11y1F8JPd9$71d86c731736792815a62178196c587df44ac4e5753008e22db75b7b9e8bbb2364963c82d21d91a1ca2a6ae99e358e9c1a044b9f8dbb73952e40c504adaffd42', NULL, 'usuario');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_actividades`
--

CREATE TABLE `usuario_actividades` (
  `usuario_id` int(11) NOT NULL,
  `actividad_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `analisis_sentimientos`
--
ALTER TABLE `analisis_sentimientos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chat_interaccion_id` (`chat_interaccion_id`),
  ADD KEY `idx_usuario_fecha` (`usuario_id`,`fecha_analisis`),
  ADD KEY `idx_nivel_riesgo` (`nivel_riesgo`);

--
-- Indices de la tabla `avatar_config`
--
ALTER TABLE `avatar_config`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `avatar_logs`
--
ALTER TABLE `avatar_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_usuario_id` (`usuario_id`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indices de la tabla `chat_analytics`
--
ALTER TABLE `chat_analytics`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_fecha` (`fecha`);

--
-- Indices de la tabla `chat_interacciones`
--
ALTER TABLE `chat_interacciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `idx_crisis` (`is_crisis`,`crisis_level`),
  ADD KEY `idx_chat_fecha` (`fecha`),
  ADD KEY `idx_chat_sentimiento` (`sentimiento`),
  ADD KEY `idx_chat_usuario` (`usuario_id`);

--
-- Indices de la tabla `chat_temas`
--
ALTER TABLE `chat_temas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_tema` (`tema`);

--
-- Indices de la tabla `interacciones`
--
ALTER TABLE `interacciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `tipo_interaccion_id` (`tipo_interaccion_id`),
  ADD KEY `nivel_riesgo_id` (`nivel_riesgo_id`);

--
-- Indices de la tabla `nivel_riesgo`
--
ALTER TABLE `nivel_riesgo`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nivel` (`nivel`);

--
-- Indices de la tabla `notificaciones_admin`
--
ALTER TABLE `notificaciones_admin`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `chat_interaccion_id` (`chat_interaccion_id`),
  ADD KEY `idx_notif_leida` (`leida`),
  ADD KEY `idx_notif_tipo` (`tipo`),
  ADD KEY `idx_notif_fecha` (`fecha_creacion`);

--
-- Indices de la tabla `password_resets`
--
ALTER TABLE `password_resets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `token` (`token`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `recursos_apoyo`
--
ALTER TABLE `recursos_apoyo`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `riesgo`
--
ALTER TABLE `riesgo`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `seguimiento_emocional`
--
ALTER TABLE `seguimiento_emocional`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `estado_emo_id` (`estado_emo_id`);

--
-- Indices de la tabla `sesiones_juego`
--
ALTER TABLE `sesiones_juego`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `tareas`
--
ALTER TABLE `tareas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_tareas_usuario` (`usuario_id`);

--
-- Indices de la tabla `tendencias_semanales`
--
ALTER TABLE `tendencias_semanales`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_fecha` (`fecha`),
  ADD KEY `idx_fecha` (`fecha`);

--
-- Indices de la tabla `tipo_interaccion`
--
ALTER TABLE `tipo_interaccion`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `user_streaks`
--
ALTER TABLE `user_streaks`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_date` (`user_id`,`fecha`);

--
-- Indices de la tabla `user_streak_stats`
--
ALTER TABLE `user_streak_stats`
  ADD PRIMARY KEY (`user_id`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `correo` (`correo`),
  ADD KEY `canal_preferido_id` (`canal_preferido_id`),
  ADD KEY `estado_emo_actual_id` (`estado_emo_actual_id`),
  ADD KEY `nivel_riesgo_act_id` (`nivel_riesgo_act_id`),
  ADD KEY `idx_usuario_updated` (`updated_at`);

--
-- Indices de la tabla `usuario_actividades`
--
ALTER TABLE `usuario_actividades`
  ADD PRIMARY KEY (`usuario_id`,`actividad_id`),
  ADD KEY `actividad_id` (`actividad_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `analisis_sentimientos`
--
ALTER TABLE `analisis_sentimientos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `avatar_config`
--
ALTER TABLE `avatar_config`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `avatar_logs`
--
ALTER TABLE `avatar_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `chat_analytics`
--
ALTER TABLE `chat_analytics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `chat_interacciones`
--
ALTER TABLE `chat_interacciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- AUTO_INCREMENT de la tabla `chat_temas`
--
ALTER TABLE `chat_temas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `interacciones`
--
ALTER TABLE `interacciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `nivel_riesgo`
--
ALTER TABLE `nivel_riesgo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `notificaciones_admin`
--
ALTER TABLE `notificaciones_admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `password_resets`
--
ALTER TABLE `password_resets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `recursos_apoyo`
--
ALTER TABLE `recursos_apoyo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `riesgo`
--
ALTER TABLE `riesgo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `seguimiento_emocional`
--
ALTER TABLE `seguimiento_emocional`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sesiones_juego`
--
ALTER TABLE `sesiones_juego`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `tareas`
--
ALTER TABLE `tareas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT de la tabla `tendencias_semanales`
--
ALTER TABLE `tendencias_semanales`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tipo_interaccion`
--
ALTER TABLE `tipo_interaccion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `user_streaks`
--
ALTER TABLE `user_streaks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `analisis_sentimientos`
--
ALTER TABLE `analisis_sentimientos`
  ADD CONSTRAINT `analisis_sentimientos_ibfk_1` FOREIGN KEY (`chat_interaccion_id`) REFERENCES `chat_interacciones` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `analisis_sentimientos_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `avatar_logs`
--
ALTER TABLE `avatar_logs`
  ADD CONSTRAINT `avatar_logs_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `interacciones`
--
ALTER TABLE `interacciones`
  ADD CONSTRAINT `interacciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `interacciones_ibfk_2` FOREIGN KEY (`tipo_interaccion_id`) REFERENCES `tipo_interaccion` (`id`),
  ADD CONSTRAINT `interacciones_ibfk_3` FOREIGN KEY (`nivel_riesgo_id`) REFERENCES `nivel_riesgo` (`id`);

--
-- Filtros para la tabla `notificaciones_admin`
--
ALTER TABLE `notificaciones_admin`
  ADD CONSTRAINT `notificaciones_admin_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `notificaciones_admin_ibfk_2` FOREIGN KEY (`chat_interaccion_id`) REFERENCES `chat_interacciones` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `password_resets`
--
ALTER TABLE `password_resets`
  ADD CONSTRAINT `password_resets_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `seguimiento_emocional`
--
ALTER TABLE `seguimiento_emocional`
  ADD CONSTRAINT `seguimiento_emocional_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `seguimiento_emocional_ibfk_2` FOREIGN KEY (`estado_emo_id`) REFERENCES `estado_emocional` (`id`);

--
-- Filtros para la tabla `tareas`
--
ALTER TABLE `tareas`
  ADD CONSTRAINT `fk_tareas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `user_streaks`
--
ALTER TABLE `user_streaks`
  ADD CONSTRAINT `user_streaks_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `user_streak_stats`
--
ALTER TABLE `user_streak_stats`
  ADD CONSTRAINT `user_streak_stats_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`canal_preferido_id`) REFERENCES `tipo_interaccion` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `usuario_ibfk_2` FOREIGN KEY (`estado_emo_actual_id`) REFERENCES `estado_emocional` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `usuario_ibfk_3` FOREIGN KEY (`nivel_riesgo_act_id`) REFERENCES `nivel_riesgo` (`id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `usuario_actividades`
--
ALTER TABLE `usuario_actividades`
  ADD CONSTRAINT `usuario_actividades_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `usuario_actividades_ibfk_2` FOREIGN KEY (`actividad_id`) REFERENCES `actividades` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
