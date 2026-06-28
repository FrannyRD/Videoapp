"""
Biblioteca inicial de contenido por página.

No genera contenido con IA en tiempo real: deja cargado un banco editable para que la app
pueda separar páginas, saber qué video sigue y cargar guiones/keywords sin mezclar nichos.
"""
from __future__ import annotations

from copy import deepcopy

PAGES = [
    {
        "id": "casos_sin_resolver",
        "name": "Casos Sin Resolver",
        "emoji": "🕵️",
        "niche": "true_crime",
        "voice": "mexico_hombre",
        "music": "true_crime",
        "subtitle_style": "cinematic",
        "description": "Casos reales, desapariciones e investigaciones que siguen dejando preguntas abiertas.",
    },
    {
        "id": "mundo_animal_salvaje",
        "name": "Mundo Animal Salvaje",
        "emoji": "🐆",
        "niche": "wildlife",
        "voice": "mexico_hombre",
        "music": "wildlife",
        "subtitle_style": "yellow",
        "description": "Comportamientos animales sorprendentes, supervivencia y naturaleza extrema sin contenido gráfico.",
    },
    {
        "id": "historia_prohibida",
        "name": "Historia Prohibida",
        "emoji": "📜",
        "niche": "history",
        "voice": "mexico_hombre",
        "music": "historical",
        "subtitle_style": "cinematic",
        "description": "Hechos históricos poco contados, documentos, decisiones y operaciones reales.",
    },
    {
        "id": "mente_profunda",
        "name": "Mente Profunda",
        "emoji": "🧠",
        "niche": "psychology",
        "voice": "mexico_hombre",
        "music": "psychology",
        "subtitle_style": "clean",
        "description": "Psicología y comportamiento humano explicado con historias reales, sin diagnósticos.",
    },
    {
        "id": "enigma_diario",
        "name": "Enigma Diario",
        "emoji": "🌀",
        "niche": "mystery",
        "voice": "mexico_hombre",
        "music": "enigma",
        "subtitle_style": "meme",
        "description": "Misterios, relatos extraños y curiosidades narradas con enfoque prudente y visual.",
    },
    {
        "id": "biblia_cinematica",
        "name": "Biblia Cinemática",
        "emoji": "✨",
        "niche": "bible",
        "voice": "mexico_hombre",
        "music": "biblical",
        "subtitle_style": "cinematic",
        "description": "Relatos bíblicos recreados de forma visual, respetuosa, educativa y emocional.",
    },
]

# Temas base de la semana. Cada tema crea 4 videos: gancho corto, historia larga, mini dato e interacción.
THEMES = {
    "casos_sin_resolver": [
        {
            "day": "Lunes", "topic": "D.B. Cooper", "type_label": "caso real / misterio aéreo",
            "angle": "el pasajero que secuestró un avión, pidió dinero y desapareció después de saltar en paracaídas",
            "known": "En 1971, un hombre que usó el nombre Dan Cooper abordó un vuelo en Estados Unidos. Tras entregar una nota, recibió dinero y paracaídas. Luego saltó del avión durante la noche y nunca fue identificado de forma definitiva.",
            "care": "No se sabe con certeza si sobrevivió al salto ni cuál fue su identidad real.",
            "keywords": ["vintage airplane night", "airport runway 1970", "dark forest rain", "old suitcase money", "police archive documents", "airplane cabin empty", "parachute silhouette", "newspaper archive"],
            "hashtags": ["#CasosSinResolver", "#MisterioReal", "#HistoriasReales", "#TrueCrime"],
        },
        {
            "day": "Martes", "topic": "Maura Murray", "type_label": "desaparición real",
            "angle": "la joven que tuvo un accidente en una carretera y desapareció antes de que llegara la policía",
            "known": "En 2004, Maura Murray sufrió un accidente de auto en New Hampshire. Un vecino llamó a la policía, pero cuando las autoridades llegaron, ella ya no estaba. Desde entonces, el caso continúa abierto.",
            "care": "Las teorías son muchas, pero ninguna ha cerrado el caso de manera definitiva.",
            "keywords": ["snowy road night", "abandoned car road", "police lights dark road", "forest winter path", "old map close up", "empty highway", "missing poster wall", "cold night trees"],
            "hashtags": ["#CasosSinResolver", "#Desaparicion", "#MisterioReal", "#HistoriasReales"],
        },
        {
            "day": "Miércoles", "topic": "El Zodiaco", "type_label": "caso policial histórico",
            "angle": "el asesino que enviaba cartas y códigos mientras la policía intentaba identificarlo",
            "known": "Entre finales de los años sesenta y principios de los setenta, el caso del Zodiaco generó miedo por sus cartas, símbolos y mensajes cifrados. Algunas piezas se han descifrado, pero su identidad sigue sin confirmarse oficialmente.",
            "care": "No conviene presentar teorías como hechos: oficialmente el caso conserva preguntas abiertas.",
            "keywords": ["old letters desk", "cipher code paper", "vintage newspaper", "detective board", "typewriter close up", "dark city street", "police archive", "magnifying glass document"],
            "hashtags": ["#CasosSinResolver", "#Misterio", "#Investigacion", "#TrueCrime"],
        },
        {
            "day": "Jueves", "topic": "JonBenét Ramsey", "type_label": "caso mediático real",
            "angle": "un caso familiar que se volvió nacional y todavía genera preguntas por sus contradicciones",
            "known": "En 1996, la muerte de JonBenét Ramsey conmocionó a Estados Unidos. La investigación incluyó una escena compleja, una nota extensa y años de análisis público. Aún hoy, muchas preguntas siguen abiertas.",
            "care": "Tratar el caso con respeto, sin imágenes sensibles ni acusaciones no probadas.",
            "keywords": ["suburban house winter", "police tape outside house", "old newspaper archive", "document on table", "quiet neighborhood snow", "detective notes", "closed door hallway", "family photo blurred"],
            "hashtags": ["#CasosSinResolver", "#CasoReal", "#MisterioReal", "#HistoriasReales"],
        },
        {
            "day": "Viernes", "topic": "Los niños Beaumont", "type_label": "desaparición histórica",
            "angle": "tres hermanos que fueron a la playa y nunca regresaron",
            "known": "En 1966, los niños Beaumont desaparecieron en Australia después de ir a la playa. Hubo testigos, búsquedas y múltiples líneas de investigación, pero nunca se encontró una respuesta definitiva.",
            "care": "Evitar detalles morbosos y enfocarse en la cronología y las preguntas del caso.",
            "keywords": ["empty beach vintage", "old bus stop", "coastal town street", "missing poster", "family archive photo blurred", "beach waves empty", "police search beach", "old newspaper clippings"],
            "hashtags": ["#CasosSinResolver", "#Desapariciones", "#MisteriosReales", "#HistoriaReal"],
        },
        {
            "day": "Sábado", "topic": "Asha Degree", "type_label": "desaparición real",
            "angle": "la niña que salió de casa durante la madrugada y fue vista caminando bajo la lluvia",
            "known": "En el año 2000, Asha Degree desapareció en Carolina del Norte. Algunas personas dijeron haberla visto caminando por una carretera de madrugada. Años después aparecieron objetos que podrían estar relacionados con el caso.",
            "care": "Mantener tono documental y no usar recreaciones violentas.",
            "keywords": ["rainy road night", "empty highway storm", "school backpack close up", "flashlight search forest", "police car lights", "country road dawn", "missing poster", "dark trees rain"],
            "hashtags": ["#CasosSinResolver", "#DesaparicionReal", "#Misterio", "#HistoriasReales"],
        },
        {
            "day": "Domingo", "topic": "Springfield Three", "type_label": "desaparición sin resolver",
            "angle": "tres mujeres que desaparecieron de una casa sin señales claras de qué ocurrió",
            "known": "En 1992, tres mujeres desaparecieron en Springfield, Missouri. La casa no mostraba una explicación evidente, y con el paso del tiempo el caso se convirtió en uno de los misterios más conocidos de la zona.",
            "care": "No afirmar teorías como certezas; cerrar con pregunta abierta.",
            "keywords": ["empty house night", "quiet street lamps", "old telephone close up", "detective board", "police search neighborhood", "dark living room", "archive folders", "porch light night"],
            "hashtags": ["#CasosSinResolver", "#CasoReal", "#MisterioReal", "#TrueCrime"],
        },
    ],
    "mundo_animal_salvaje": [
        {"day": "Lunes", "topic": "Orcas", "type_label": "depredadores inteligentes", "angle": "la estrategia de caza coordinada de las orcas", "known": "Las orcas son depredadores altamente sociales. Algunas poblaciones cazan en grupo, se comunican y aprenden técnicas específicas que se transmiten dentro de su grupo.", "care": "Mostrar naturaleza extrema sin escenas sangrientas.", "keywords": ["orca ocean", "killer whale pod", "cold ocean waves", "marine wildlife", "seal ocean distance", "whale fin water", "arctic sea", "ocean documentary"], "hashtags": ["#MundoAnimal", "#NaturalezaSalvaje", "#Animales", "#VidaSalvaje"]},
        {"day": "Martes", "topic": "Pulpos", "type_label": "inteligencia animal", "angle": "el animal que puede resolver problemas, esconderse y cambiar su apariencia", "known": "Los pulpos son conocidos por su inteligencia, su capacidad de camuflaje y su habilidad para escapar de espacios complejos. Su comportamiento sorprende porque combina memoria, flexibilidad y defensa visual.", "care": "Enfocarse en ciencia y asombro.", "keywords": ["octopus underwater", "coral reef octopus", "ocean camouflage", "aquarium octopus", "underwater rocks", "marine life close up", "blue ocean reef", "sea creature"], "hashtags": ["#MundoAnimal", "#AnimalesCuriosos", "#Naturaleza", "#VidaMarina"]},
        {"day": "Miércoles", "topic": "Cocodrilos", "type_label": "supervivencia extrema", "angle": "uno de los depredadores más antiguos y pacientes del planeta", "known": "Los cocodrilos han sobrevivido durante millones de años gracias a su resistencia, su paciencia y su forma de ahorrar energía. Son animales adaptados a esperar el momento preciso.", "care": "No usar ataques gráficos; usar tomas de agua, ojos y movimiento.", "keywords": ["crocodile water", "alligator eyes", "swamp wildlife", "river jungle", "reptile close up", "wetlands nature", "crocodile swimming", "dark river"], "hashtags": ["#MundoAnimal", "#Depredadores", "#NaturalezaExtrema", "#AnimalesSalvajes"]},
        {"day": "Jueves", "topic": "Águilas", "type_label": "aves cazadoras", "angle": "la precisión visual y de vuelo de las águilas", "known": "Las águilas poseen una visión excepcional y un vuelo poderoso. Su capacidad para detectar movimiento a distancia las convierte en cazadoras muy eficientes dentro de su ecosistema.", "care": "Mostrar caza de forma documental y no explícita.", "keywords": ["eagle flying", "eagle eyes close up", "mountain sky bird", "bird of prey", "eagle nest", "wild bird slow motion", "rocky mountains", "sky wings"], "hashtags": ["#MundoAnimal", "#AvesRapaces", "#Naturaleza", "#VidaSalvaje"]},
        {"day": "Viernes", "topic": "Lobos", "type_label": "estrategia de manada", "angle": "la coordinación que hace fuerte a una manada", "known": "Los lobos viven en grupos con jerarquías y cooperación. Su éxito no depende solo de la fuerza, sino de la comunicación, la resistencia y el trabajo en equipo.", "care": "Evitar escenas violentas; usar manada, bosque y nieve.", "keywords": ["wolves forest", "wolf pack snow", "wolf eyes", "winter forest wildlife", "howling wolf", "mountain forest", "wild canines", "snow landscape"], "hashtags": ["#MundoAnimal", "#Lobos", "#NaturalezaSalvaje", "#Animales"]},
        {"day": "Sábado", "topic": "Tiburones", "type_label": "océano extremo", "angle": "un depredador marino más antiguo de lo que muchos imaginan", "known": "Los tiburones existen desde hace cientos de millones de años. Sus sentidos, su movimiento y su papel en el equilibrio marino los vuelven piezas clave del océano.", "care": "Evitar sangre y ataques; enfocarse en datos y conservación.", "keywords": ["shark underwater", "great white shark", "deep blue ocean", "shark fin water", "marine predator", "ocean documentary", "coral reef fish", "underwater camera"], "hashtags": ["#MundoAnimal", "#Tiburones", "#VidaMarina", "#Naturaleza"]},
        {"day": "Domingo", "topic": "Camaleones", "type_label": "adaptación animal", "angle": "el animal que usa color, paciencia y precisión para sobrevivir", "known": "Los camaleones son famosos por cambiar de color, pero también por sus ojos móviles, su lengua rápida y su forma paciente de cazar. Su cuerpo está diseñado para ahorrar energía y pasar desapercibido.", "care": "Visual, curioso y educativo.", "keywords": ["chameleon close up", "green lizard leaves", "reptile camouflage", "rainforest leaves", "lizard eye close up", "macro wildlife", "tropical forest", "insect on leaf"], "hashtags": ["#MundoAnimal", "#AnimalesCuriosos", "#Naturaleza", "#VidaSalvaje"]},
    ],
    "historia_prohibida": [
        {"day": "Lunes", "topic": "Operación Mincemeat", "type_label": "operación real", "angle": "el engaño que ayudó a cambiar una campaña militar", "known": "Durante la Segunda Guerra Mundial, los Aliados usaron documentos falsos para confundir a las fuerzas alemanas sobre el lugar de una invasión. La operación es un ejemplo real de inteligencia, planificación y desinformación militar.", "care": "Presentar como hecho histórico documentado, sin conspiraciones.", "keywords": ["world war archive", "old military documents", "vintage map table", "secret files", "navy officer archive", "typewriter war", "old envelope", "military planning room"], "hashtags": ["#HistoriaProhibida", "#HistoriaReal", "#SegundaGuerra", "#Documental"]},
        {"day": "Martes", "topic": "Batalla del Castillo Itter", "type_label": "hecho histórico poco contado", "angle": "la batalla donde enemigos terminaron luchando del mismo lado", "known": "En los últimos días de la Segunda Guerra Mundial ocurrió una situación inusual en el Castillo Itter: soldados estadounidenses y antiguos enemigos colaboraron para defender a prisioneros franceses. Es uno de esos episodios que parecen ficción, pero está documentado.", "care": "Tono documental y preciso.", "keywords": ["old castle europe", "world war soldiers", "historic castle fog", "military archive", "stone fortress", "old battlefield", "vintage war map", "europe mountains"], "hashtags": ["#HistoriaProhibida", "#HistoriaReal", "#Guerra", "#Documental"]},
        {"day": "Miércoles", "topic": "MK-Ultra", "type_label": "programa desclasificado", "angle": "un programa real de experimentación que fue investigado años después", "known": "MK-Ultra fue un programa de la CIA que incluyó investigaciones sobre control mental y sustancias. Décadas después, investigaciones oficiales revelaron parte de lo ocurrido, aunque muchos documentos fueron destruidos.", "care": "No exagerar ni convertirlo en teoría; usar lenguaje verificable.", "keywords": ["declassified documents", "old laboratory", "secret government files", "vintage office", "archive boxes", "typewriter document", "dark research room", "confidential stamp"], "hashtags": ["#HistoriaProhibida", "#DocumentosDesclasificados", "#HistoriaReal", "#CIA"]},
        {"day": "Jueves", "topic": "Operación Paperclip", "type_label": "decisión histórica polémica", "angle": "la operación que llevó científicos alemanes a Estados Unidos después de la guerra", "known": "Después de la Segunda Guerra Mundial, Estados Unidos reclutó a científicos alemanes mediante la Operación Paperclip. El objetivo era aprovechar conocimientos técnicos en plena competencia científica y militar de la posguerra.", "care": "Explicar contexto y polémica sin glorificar a nadie.", "keywords": ["rocket scientist archive", "old nasa rocket", "declassified file", "post war documents", "vintage laboratory", "military office", "cold war map", "old rocket launch"], "hashtags": ["#HistoriaProhibida", "#GuerraFria", "#HistoriaReal", "#Documental"]},
        {"day": "Viernes", "topic": "Incidente de Gleiwitz", "type_label": "operación de bandera falsa", "angle": "el ataque usado como pretexto antes de una invasión", "known": "El incidente de Gleiwitz fue una acción organizada por la Alemania nazi en 1939 para simular una agresión polaca. Fue utilizado como parte de la justificación propagandística antes de la invasión de Polonia.", "care": "Hecho histórico serio; evitar sensacionalismo.", "keywords": ["radio tower night", "1930s archive", "old propaganda newspaper", "border checkpoint", "military documents", "vintage radio station", "europe map old", "black and white street"], "hashtags": ["#HistoriaProhibida", "#HistoriaReal", "#SegundaGuerra", "#Documental"]},
        {"day": "Sábado", "topic": "Telegrama Zimmermann", "type_label": "documento histórico", "angle": "el mensaje interceptado que ayudó a cambiar el rumbo de una guerra", "known": "En 1917, un telegrama alemán enviado a México fue interceptado y descifrado por inteligencia británica. Su contenido influyó en la opinión pública y en el ingreso de Estados Unidos a la Primera Guerra Mundial.", "care": "Explicar sin hacerlo académico.", "keywords": ["old telegram", "world war one map", "code breaking room", "vintage documents", "old radio communication", "archive desk", "diplomatic papers", "historic newspaper"], "hashtags": ["#HistoriaProhibida", "#PrimeraGuerra", "#HistoriaReal", "#Archivos"]},
        {"day": "Domingo", "topic": "Operación Northwoods", "type_label": "documento desclasificado", "angle": "un plan propuesto que fue rechazado antes de ejecutarse", "known": "Operación Northwoods fue una propuesta de 1962 dentro del contexto de la Guerra Fría. Los documentos desclasificados muestran planes polémicos que finalmente no fueron aprobados por el presidente John F. Kennedy.", "care": "Aclarar que fue propuesta, no operación ejecutada.", "keywords": ["declassified papers", "cold war office", "pentagon archive", "old typewriter", "1960s documents", "confidential stamp", "military planning", "washington archive"], "hashtags": ["#HistoriaProhibida", "#DocumentosDesclasificados", "#GuerraFria", "#HistoriaReal"]},
    ],
    "mente_profunda": [
        {"day": "Lunes", "topic": "Efecto espectador", "type_label": "psicología social", "angle": "por qué a veces muchas personas mirando no significa más ayuda", "known": "El efecto espectador describe cómo, en ciertas situaciones, las personas pueden tardar más en actuar cuando hay otros presentes, porque la responsabilidad se reparte mentalmente entre el grupo.", "care": "No culpar a personas; explicar el patrón con respeto.", "keywords": ["crowd street slow motion", "people watching city", "urban crosswalk", "lonely person bench", "group psychology", "busy train station", "hands hesitating", "city night people"], "hashtags": ["#MenteProfunda", "#Psicologia", "#ComportamientoHumano", "#Reflexion"]},
        {"day": "Martes", "topic": "Obediencia a la autoridad", "type_label": "experimento psicológico", "angle": "por qué una orden puede hacer que alguien dude de su propio criterio", "known": "Experimentos sobre obediencia mostraron que muchas personas pueden seguir instrucciones incómodas cuando una figura de autoridad insiste. El punto no es juzgar, sino entender la presión psicológica del contexto.", "care": "No recrear daño; explicar de forma educativa.", "keywords": ["old laboratory", "scientist clipboard", "person thinking dark room", "experiment room", "authority figure silhouette", "hands nervous", "vintage psychology", "empty chair"], "hashtags": ["#MenteProfunda", "#PsicologiaSocial", "#ConductaHumana", "#Experimentos"]},
        {"day": "Miércoles", "topic": "Sesgo de confirmación", "type_label": "sesgo cognitivo", "angle": "la razón por la que buscamos pruebas que confirmen lo que ya creemos", "known": "El sesgo de confirmación ocurre cuando prestamos más atención a la información que coincide con nuestras ideas previas y rechazamos más rápido lo que las contradice.", "care": "Evitar atacar creencias; enfoque reflexivo.", "keywords": ["person scrolling phone", "social media feed", "thinking face close up", "notes on wall", "decision making", "news headlines", "mirror reflection", "mind concept"], "hashtags": ["#MenteProfunda", "#SesgosCognitivos", "#Psicologia", "#Reflexion"]},
        {"day": "Jueves", "topic": "Efecto halo", "type_label": "percepción social", "angle": "cómo una primera impresión puede cambiar todo lo que creemos de alguien", "known": "El efecto halo aparece cuando una característica positiva o negativa influye en cómo interpretamos el resto de una persona. Por eso una buena impresión puede pesar más de lo que imaginamos.", "care": "No diagnosticar ni etiquetar personas.", "keywords": ["first impression handshake", "people meeting office", "portrait shadow", "mirror face", "social perception", "elegant person walking", "crowd blurred", "thinking woman window"], "hashtags": ["#MenteProfunda", "#Comportamiento", "#Psicologia", "#MenteHumana"]},
        {"day": "Viernes", "topic": "Indefensión aprendida", "type_label": "aprendizaje psicológico", "angle": "cuando una persona deja de intentar porque aprendió que nada cambia", "known": "La indefensión aprendida describe cómo, después de experiencias repetidas de falta de control, alguien puede dejar de intentar cambiar una situación incluso cuando aparecen nuevas opciones.", "care": "No dar consejo médico; cerrar con reflexión general.", "keywords": ["person alone room", "rain window", "empty chair", "walking alone street", "dark hallway", "sunrise hope", "hands on table", "quiet bedroom"], "hashtags": ["#MenteProfunda", "#Psicologia", "#Emociones", "#Reflexion"]},
        {"day": "Sábado", "topic": "Presión social", "type_label": "experimento social", "angle": "por qué a veces sabemos la respuesta, pero seguimos al grupo", "known": "Los estudios sobre conformidad muestran que una persona puede cambiar su respuesta para no sentirse fuera del grupo, incluso cuando en el fondo cree que el grupo está equivocado.", "care": "Explicar sin humillar ni juzgar.", "keywords": ["group of people", "classroom experiment", "person nervous crowd", "hands raised", "team meeting", "standing alone", "social pressure", "people pointing board"], "hashtags": ["#MenteProfunda", "#PresionSocial", "#PsicologiaSocial", "#Comportamiento"]},
        {"day": "Domingo", "topic": "Experimento de la prisión", "type_label": "historia real / psicología", "angle": "el experimento que se detuvo antes de tiempo por cómo cambiaron los roles", "known": "En 1971, el experimento de la prisión de Stanford dividió participantes en roles de guardias y prisioneros. La situación se deterioró tan rápido que fue suspendido antes de lo previsto.", "care": "No presentarlo como prueba absoluta; mencionar que ha sido debatido y revisado.", "keywords": ["empty prison hallway", "vintage university", "psychology experiment", "closed door corridor", "student group", "old archive documents", "serious man thinking", "shadow bars"], "hashtags": ["#MenteProfunda", "#Psicologia", "#ExperimentoSocial", "#ConductaHumana"]},
    ],
    "enigma_diario": [
        {"day": "Lunes", "topic": "Faro de Flannan Isles", "type_label": "misterio histórico", "angle": "tres fareros desaparecieron y el faro quedó en silencio", "known": "En 1900, tres fareros desaparecieron de las islas Flannan. Las investigaciones encontraron un faro vacío y preguntas que siguen siendo parte de uno de los relatos marítimos más conocidos.", "care": "Tratar como misterio histórico, sin exagerar teorías.", "keywords": ["lighthouse storm", "foggy island", "ocean waves rocks", "old lighthouse door", "ship approaching coast", "dark sea", "empty room candle", "storm clouds"], "hashtags": ["#EnigmaDiario", "#Misterios", "#HistoriasReales", "#Curiosidades"]},
        {"day": "Martes", "topic": "Ourang Medan", "type_label": "relato marítimo", "angle": "el barco fantasma del que se habla desde hace décadas", "known": "El Ourang Medan es un relato marítimo repetido durante décadas sobre un barco encontrado en condiciones extrañas. La historia es famosa, pero sus fuentes y detalles han sido debatidos.", "care": "Aclarar que es relato debatido, no hecho confirmado en todos sus detalles.", "keywords": ["abandoned ship fog", "cargo ship ocean", "stormy sea", "old radio room", "dark ship deck", "maritime archive", "sea mist", "empty corridor ship"], "hashtags": ["#EnigmaDiario", "#Misterio", "#Barcos", "#Relatos"]},
        {"day": "Miércoles", "topic": "El niño que recordaba otra vida", "type_label": "relato curioso", "angle": "un caso contado como si la memoria viniera de otro lugar", "known": "Existen relatos de niños que aseguran recordar detalles de una vida anterior. Algunos han sido investigados por curiosidad cultural y psicológica, aunque no existe una explicación única aceptada por todos.", "care": "No afirmar como prueba sobrenatural; usar enfoque de misterio cultural.", "keywords": ["child looking window", "old family photo", "foggy village", "notebook writing", "quiet bedroom", "memory concept", "old house", "soft light portrait"], "hashtags": ["#EnigmaDiario", "#Misterios", "#HistoriasCuriosas", "#Relatos"]},
        {"day": "Jueves", "topic": "La habitación que nadie quería limpiar", "type_label": "historia misteriosa", "angle": "una habitación de hotel que acumuló rumores por lo que ocurrió dentro", "known": "Algunas historias de hoteles se vuelven leyenda por detalles repetidos, habitaciones cerradas y testimonios difíciles de verificar. Lo importante es separar el relato del hecho confirmado.", "care": "Evitar afirmaciones paranormales como hechos.", "keywords": ["hotel hallway dark", "empty hotel room", "old key close up", "cleaning cart hallway", "closed door", "night hotel corridor", "lamp flicker", "quiet bedroom"], "hashtags": ["#EnigmaDiario", "#Misterios", "#Relatos", "#Curiosidades"]},
        {"day": "Viernes", "topic": "El mensaje que llegó años tarde", "type_label": "curiosidad real", "angle": "una carta o mensaje encontrado mucho después de ser enviado", "known": "Hay casos reales de mensajes encontrados años después: botellas, cartas perdidas o paquetes que llegan tarde. Cada uno recuerda que a veces el tiempo convierte algo simple en misterio.", "care": "Usar como relato emocional, no conspirativo.", "keywords": ["message in bottle", "old letter", "ocean shore", "hands opening letter", "post office vintage", "wooden desk paper", "sea waves beach", "old envelope"], "hashtags": ["#EnigmaDiario", "#HistoriasCuriosas", "#Misterios", "#RelatosReales"]},
        {"day": "Sábado", "topic": "Santuario de Ise", "type_label": "misterio cultural", "angle": "el templo que se reconstruye una y otra vez para conservar su esencia", "known": "El Santuario de Ise en Japón es conocido por una tradición de reconstrucción periódica. Más que un misterio paranormal, es una forma cultural de conservar continuidad, oficio y memoria.", "care": "Respetar el valor cultural y espiritual.", "keywords": ["japanese shrine forest", "wood temple japan", "shinto shrine", "forest path japan", "traditional carpentry", "sunlight trees", "wooden architecture", "quiet temple"], "hashtags": ["#EnigmaDiario", "#Cultura", "#Misterios", "#Historias"]},
        {"day": "Domingo", "topic": "Experimento de la prisión", "type_label": "experimento debatido", "angle": "un estudio que mostró cómo un rol puede cambiar la conducta", "known": "El experimento de la prisión de Stanford se volvió famoso porque fue detenido antes de lo esperado. También ha sido debatido por sus métodos y conclusiones, por eso conviene contarlo con cuidado.", "care": "Presentarlo como experimento histórico debatido, no como verdad absoluta.", "keywords": ["empty prison hallway", "university archive", "psychology documents", "student group", "closed corridor", "old camera footage", "shadow bars", "serious classroom"], "hashtags": ["#EnigmaDiario", "#Psicologia", "#Misterios", "#HistoriasReales"]},
    ],
    "biblia_cinematica": [
        {"day": "Lunes", "topic": "Daniel en el foso", "type_label": "relato bíblico", "angle": "la fe de Daniel frente al miedo", "known": "El relato de Daniel muestra a un hombre que conserva su fe incluso cuando enfrenta una prueba extrema. La fuerza de la historia está en la confianza, la calma y la esperanza.", "care": "Recreación visual inspirada en relatos bíblicos, respetuosa y no gráfica.", "keywords": ["ancient stone room", "lion shadow", "candle light cave", "old parchment", "desert night", "praying man silhouette", "ancient palace", "warm cinematic light"], "hashtags": ["#BibliaCinematica", "#HistoriasBiblicas", "#Fe", "#RelatosBiblicos"]},
        {"day": "Martes", "topic": "Noé y el arca", "type_label": "relato bíblico", "angle": "obedecer cuando nadie entiende el propósito", "known": "La historia de Noé habla de obediencia, paciencia y esperanza en medio de una gran prueba. Es un relato sobre preparación y confianza.", "care": "Usar imágenes simbólicas, agua, madera, lluvia y luz.", "keywords": ["wooden boat rain", "storm clouds", "animals silhouette", "ancient wood", "rain window", "flood water", "dove flying", "sunlight after storm"], "hashtags": ["#BibliaCinematica", "#Noe", "#Fe", "#HistoriasBiblicas"]},
        {"day": "Miércoles", "topic": "Jonás", "type_label": "relato bíblico", "angle": "huir de un llamado y terminar enfrentando el silencio", "known": "El relato de Jonás habla de desobediencia, reflexión y una segunda oportunidad. Su fuerza está en mostrar que a veces el camino de regreso también enseña.", "care": "No mostrar escenas gráficas; usar mar, tormenta y símbolos.", "keywords": ["stormy ocean", "ancient boat", "man silhouette sea", "dark waves", "whale shadow underwater", "old sandals sand", "sunrise ocean", "prayer silhouette"], "hashtags": ["#BibliaCinematica", "#Jonas", "#Fe", "#RelatosBiblicos"]},
        {"day": "Jueves", "topic": "José", "type_label": "relato bíblico", "angle": "la traición que terminó convirtiéndose en propósito", "known": "La historia de José presenta rechazo, espera y restauración. Es un relato sobre cómo una prueba difícil puede abrir un camino inesperado.", "care": "Tono emocional y educativo.", "keywords": ["ancient desert road", "colorful fabric", "old prison cell", "egypt palace", "wheat field", "hands holding grain", "ancient market", "sunset desert"], "hashtags": ["#BibliaCinematica", "#Jose", "#HistoriasBiblicas", "#Fe"]},
        {"day": "Viernes", "topic": "Jericó", "type_label": "relato bíblico", "angle": "cuando una muralla representa una prueba de fe", "known": "El relato de Jericó es recordado por la obediencia, la perseverancia y la imagen de una muralla que cae después de un proceso. Es una historia sobre confianza y constancia.", "care": "Usar recreación simbólica, sin violencia.", "keywords": ["ancient city wall", "desert wall", "trumpet silhouette", "old stone gate", "people walking desert", "dusty road", "sunrise city", "ancient ruins"], "hashtags": ["#BibliaCinematica", "#Jerico", "#Fe", "#RelatosBiblicos"]},
        {"day": "Sábado", "topic": "Jesús camina sobre el agua", "type_label": "relato bíblico", "angle": "mirar la tormenta o mirar la fe", "known": "Este relato muestra miedo, confianza y la imagen de una fe que sostiene en medio de la tormenta. Es uno de los pasajes más visuales y emocionales del Nuevo Testamento.", "care": "Recreación visual inspirada, sin representar de forma irrespetuosa.", "keywords": ["stormy sea night", "wooden boat waves", "man silhouette water", "light over ocean", "disciples boat", "rain ocean", "calm sea sunrise", "hands reaching water"], "hashtags": ["#BibliaCinematica", "#Jesus", "#Fe", "#HistoriasBiblicas"]},
        {"day": "Domingo", "topic": "La resurrección", "type_label": "relato bíblico", "angle": "la mañana que cambió la esperanza de muchos", "known": "La resurrección es uno de los relatos centrales de la fe cristiana. Visualmente puede narrarse con silencio, piedra removida, luz de amanecer y una sensación de esperanza.", "care": "Respetuoso, emocional y sin sensacionalismo.", "keywords": ["empty tomb sunrise", "stone cave light", "linen cloth", "ancient garden", "sunrise rays", "stone rolled away", "peaceful morning", "warm holy light"], "hashtags": ["#BibliaCinematica", "#Resurreccion", "#Fe", "#HistoriasBiblicas"]},
    ],
}

VIDEO_TYPES = [
    ("gancho", "Video 1 — Dato gancho corto", "25-35 segundos"),
    ("historia_larga", "Video 2 — Historia larga", "2-3 minutos"),
    ("mini", "Video 3 — Mini dato / mini historia", "35-50 segundos"),
    ("interaccion", "Video 4 — Interacción", "15-25 segundos"),
]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]


def _safe_description(page_name: str, topic: str, type_key: str, hashtags: list[str]) -> str:
    if page_name == "Biblia Cinemática":
        base = f"Recreación visual inspirada en el relato de {topic}, con un enfoque respetuoso, educativo y cinematográfico."
    elif page_name == "Casos Sin Resolver":
        base = f"Un caso real contado con enfoque documental y respetuoso. {topic} sigue dejando preguntas que aún generan conversación."
    elif page_name == "Mundo Animal Salvaje":
        base = f"Un vistazo educativo al comportamiento de {topic} y a cómo la naturaleza puede sorprender sin necesidad de exagerar."
    elif page_name == "Historia Prohibida":
        base = f"Un hecho histórico poco contado explicado de forma clara, con contexto y sin convertir rumores en hechos."
    elif page_name == "Mente Profunda":
        base = f"Una historia para entender mejor cómo funciona la mente humana y por qué algunas conductas se repiten."
    else:
        base = f"Una historia curiosa narrada con enfoque prudente para mirar el misterio desde otra perspectiva."
    return base + "\n\n" + " ".join(hashtags[:4])


def _build_story_text(page_name: str, theme: dict) -> str:
    topic = theme["topic"]
    intro_by_page = {
        "Casos Sin Resolver": f"Hay casos que no inquietan por lo que se sabe, sino por todo lo que quedó sin explicar. El caso de {topic} es uno de ellos.",
        "Mundo Animal Salvaje": f"En la naturaleza, algunas habilidades parecen diseñadas para recordarnos que sobrevivir es una ciencia silenciosa. {topic} lo demuestra.",
        "Historia Prohibida": f"Esto casi nadie lo cuenta con calma, pero {topic} muestra cómo una decisión o documento puede cambiar mucho más de lo que parece.",
        "Mente Profunda": f"A veces creemos que actuamos con total libertad, pero la mente responde a presiones invisibles. {topic} ayuda a entenderlo.",
        "Enigma Diario": f"Hay historias que sobreviven porque no tienen una sola explicación simple. {topic} es una de esas piezas que todavía despiertan preguntas.",
        "Biblia Cinemática": f"En este relato visual inspirado en la Biblia, {topic} nos recuerda que la fe suele probarse en momentos de silencio, espera y decisión.",
    }.get(page_name, f"Esta historia sobre {topic} sigue generando curiosidad.")

    return (
        f"{intro_by_page} "
        f"{theme['known']} "
        f"Lo interesante no está solo en el dato principal, sino en el contexto. Cuando miramos la historia con cuidado, aparecen detalles que obligan a bajar el ritmo: quién estaba presente, qué se sabía en ese momento, qué se descubrió después y qué parte todavía permanece abierta. "
        f"En este tipo de contenido, lo más fuerte no siempre es gritar una respuesta. A veces lo más fuerte es seguir el hilo con calma. Primero está el hecho que todos recuerdan. Después vienen los pequeños detalles: una fecha, un documento, un testimonio, una decisión o un comportamiento que cambia la forma de mirar todo. "
        f"También hay algo importante: no todo lo que se repite en internet tiene el mismo peso. Algunas versiones son datos documentados, otras son interpretaciones, y otras simplemente son teorías que crecieron con el tiempo. Por eso conviene narrarlo con cuidado, sin convertir dudas en certezas. "
        f"Por eso este video no busca exagerar ni imponer una conclusión. Busca ordenar los hechos de forma clara y mostrar por qué {topic} sigue siendo recordado. "
        f"{theme['care']} "
        f"Si algo deja esta historia es que muchas veces el detalle más pequeño puede cambiar la percepción completa del caso. Y cuando una historia sigue viva durante años, normalmente no es por una sola pregunta, sino por todas las respuestas que nunca terminaron de aparecer. "
        f"Al final, la pregunta no es solamente qué ocurrió. La pregunta es por qué este caso, este relato o este comportamiento sigue llamando nuestra atención tanto tiempo después."
    )


def _make_scenes(theme: dict, video_type: str) -> list[dict]:
    topic = theme["topic"]
    k = theme["keywords"]
    if video_type == "gancho":
        texts = [
            f"Esto sobre {topic} todavía deja preguntas.",
            theme["angle"].capitalize() + ".",
            "Lo más extraño es que la respuesta no es tan simple.",
            "Por eso este caso sigue generando conversación.",
        ]
    elif video_type == "mini":
        parts = _sentences(theme["known"])
        texts = [
            f"Un detalle poco contado de {topic} cambia la forma de ver la historia.",
            parts[0] + "." if parts else theme["known"],
            theme["care"],
            "Ese detalle es justo lo que mantiene viva la pregunta.",
        ]
    elif video_type == "interaccion":
        texts = [
            f"Después de conocer {topic}, hay una pregunta difícil.",
            "¿Crees que la explicación más simple es suficiente?",
            "O tal vez todavía falta una pieza importante.",
            "Guarda este video para revisar la historia completa después.",
        ]
    else:
        texts = _sentences(_build_story_text("", theme))[:8]
    return [{"text": text, "keyword": k[i % len(k)]} for i, text in enumerate(texts)]


def build_content_library() -> dict:
    page_map = {p["id"]: deepcopy(p) for p in PAGES}
    for p in page_map.values():
        p["videos"] = []

    for page in PAGES:
        for day_index, theme in enumerate(THEMES[page["id"]], start=1):
            for order, (type_key, type_label, duration) in enumerate(VIDEO_TYPES, start=1):
                video_id = f"{page['id']}_{day_index:02d}_{order:02d}_{type_key}"
                is_story = type_key == "historia_larga"
                if type_key == "gancho":
                    title = f"{theme['topic']}: el dato que engancha"
                elif type_key == "historia_larga":
                    title = f"La historia de {theme['topic']}"
                elif type_key == "mini":
                    title = f"El detalle poco contado de {theme['topic']}"
                else:
                    title = f"La pregunta que deja {theme['topic']}"

                item = {
                    "id": video_id,
                    "page_id": page["id"],
                    "page_name": page["name"],
                    "day": theme["day"],
                    "day_index": day_index,
                    "order": order,
                    "type_key": type_key,
                    "type": type_label,
                    "duration": duration,
                    "topic": theme["topic"],
                    "title": title,
                    "content_type": "story" if is_story else "scenes",
                    "voice": page["voice"],
                    "music": page["music"],
                    "subtitle_style": page["subtitle_style"],
                    "keywords": theme["keywords"],
                    "scenes": _make_scenes(theme, type_key),
                    "story_text": _build_story_text(page["name"], theme),
                    "description": _safe_description(page["name"], theme["topic"], type_key, theme["hashtags"]),
                    "hashtags": theme["hashtags"][:4],
                    "notes": "Keywords pensadas para no repetir clips dentro de la página; la app además guarda historial de clips usados por Pexels.",
                }
                page_map[page["id"]]["videos"].append(item)

    return {"pages": list(page_map.values())}


CONTENT_LIBRARY = build_content_library()
