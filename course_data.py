# course_data.py

class10_data = {
    "Physics": {
        "units": {
            "1": {
                "name": "Light - Reflection and Refraction",
                "topics": {
                    "Reflection of Light": "Covers laws of reflection, image formation by plane mirrors, and basic principles.",
                    "Refraction of Light": "Explains laws of refraction, refractive index, lens formula, and magnification."
                }
            },
            "2": {
                "name": "Human Eye and Colourful World",
                "topics": {
                    "Human Eye": "Structure, function, and defects of the human eye, including corrective measures.",
                    "Colourful World": "Dispersion of light, atmospheric refraction, and scattering of light."
                }
            },
            "3": {
                "name": "Electricity",
                "topics": {
                    "Electric Current and Circuit": "Covers Ohm's Law, resistance, series and parallel circuits.",
                    "Heating Effects of Electric Current": "Electric power, heating effects, and household circuits."
                }
            },
            "4": {
                "name": "Magnetic Effects of Electric Current",
                "topics": {
                    "Magnetic Field and Field Lines": "Covers magnetic fields due to current-carrying conductors and field lines.",
                    "Electromagnetic Induction": "Force on a conductor, induced potential, AC vs DC current."
                }
            }
        }
    },
    "Chemistry": {
        "units": {
            "1": {
                "name": "Chemical Reactions and Equations",
                "topics": {
                    "Chemical Reactions": "Introduction, types of chemical reactions, and balancing equations.",
                    "Effects of Chemical Reactions": "Covers corrosion, rancidity, and real-world applications."
                }
            },
            "2": {
                "name": "Acids, Bases, and Salts",
                "topics": {
                    "Acids and Bases": "Properties, uses, and the pH scale.",
                    "Salts": "Preparation, properties, and uses of common salts."
                }
            },
            "3": {
                "name": "Metals and Non-Metals",
                "topics": {
                    "Properties of Metals and Non-Metals": "Physical and chemical properties, reactivity series.",
                    "Extraction and Uses": "Covers the extraction process and applications of metals and non-metals."
                }
            },
            "4": {
                "name": "Carbon and Its Compounds",
                "topics": {
                    "Covalent Bonding": "Versatile nature of carbon and types of covalent bonds.",
                    "Important Compounds": "Focus on ethanol, ethanoic acid, soaps, and detergents."
                }
            }
        }
    },
    "Biology": {
        "units": {
            "1": {
                "name": "Life Processes",
                "topics": {
                    "Nutrition": "Autotrophic and heterotrophic nutrition.",
                    "Respiration": "Aerobic and anaerobic respiration, human respiratory system."
                }
            },
            "2": {
                "name": "Control and Coordination",
                "topics": {
                    "Nervous System": "Structure and function of the human nervous system.",
                    "Hormonal Coordination": "Endocrine glands, hormones, and their effects."
                }
            },
            "3": {
                "name": "How Do Organisms Reproduce?",
                "topics": {
                    "Asexual Reproduction": "Examples of asexual reproduction in plants and animals.",
                    "Sexual Reproduction": "Focus on human reproductive systems and health."
                }
            },
            "4": {
                "name": "Heredity and Evolution",
                "topics": {
                    "Heredity": "Mendel's laws of inheritance and their significance.",
                    "Evolution": "Theories of evolution, speciation, and adaptation."
                }
            }
        }
    },
    "AI": {
        "units": {
            "1": {
                "name": "Introduction to AI",
                "topics": {
                    "What is AI?": "Definition, history, and applications of AI.",
                    "Types of AI": "Explains narrow AI, general AI, and super AI."
                }
            },
            "2": {
                "name": "Machine Learning",
                "topics": {
                    "Basics of Machine Learning": "Introduction to supervised, unsupervised, and reinforcement learning.",
                    "Algorithms and Models": "Focus on decision trees, neural networks, and SVMs."
                }
            },
            "3": {
                "name": "Natural Language Processing (NLP)",
                "topics": {
                    "Introduction to NLP": "Text processing, sentiment analysis, and common NLP tasks.",
                    "Chatbots and Virtual Assistants": "How chatbots work and building a simple chatbot."
                }
            },
            "4": {
                "name": "AI Ethics and Future",
                "topics": {
                    "Ethical Considerations": "Bias, privacy concerns, and the impact of AI on society.",
                    "Future of AI": "Emerging trends and career opportunities in AI."
                }
            }
        }
    }
}


def get_class10_subjects():
    """
    Returns a list of subjects for Class 10.
    Example: ["Physics", "Chemistry", "Biology", "AI"]
    """
    return list(class10_data.keys())


def get_class10_units(subject: str):
    """
    Returns the units (unit_number -> {name, topics}) for a given subject.
    Example:
      {
        "1": {
          "name": "Light - Reflection and Refraction",
          "topics": {
            "Reflection of Light": "Description of topic",
            ...
          }
        },
        ...
      }
    """
    if subject in class10_data:
        return class10_data[subject]["units"]
    return {}


def build_llm_prompt(subject: str, unit_number: str, topic: str):
    """
    Constructs a pre-defined prompt for the LLM based on the user's selection.
    Example:
      Subject: Physics
      Unit: 1 - Light - Reflection and Refraction
      Topic: Reflection of Light
    """
    if subject not in class10_data:
        return "Invalid subject."
    units = class10_data[subject]["units"]
    if unit_number not in units:
        return "Invalid unit number."
    topics = units[unit_number]["topics"]
    if topic not in topics:
        return "Invalid topic."

    return (
        f"You are teaching Class 10 {subject}.\n"
        f"The current unit is '{units[unit_number]['name']}', and the topic is '{topic}'.\n\n"
        f"Please provide an engaging and detailed explanation about the topic '{topic}', "
        f"and suggest further related topics for the user to explore.\n"
    )
