intent_prompt = (
            "Determine the user's intent. Respond with a valid JSON object strictly following this format:\n"
            "```json\n"
            "{format_instruction}\n"
            "```\n\n"
            "User Input: {user_input}\n\n"
            "Only return a properly formatted JSON object without any extra text."
        )


details_prompt = (
            "Extract ticket details: name, phone, from (source), to (destination), and date.\n"
            "If details are missing, return a field called 'reply' listing the missing details.\n"
            "Strictly return a JSON object matching this format:\n"
            "```json\n"
            "{format_instruction}\n"
            "```\n\n"
            "User Input: {user_input}\n"
            "Do not add any extra text before or after the JSON object."
        )


fallback_prompt = (
            "User Input: {user_input}\n"
            "Keep me interested in traveling through trains in India.\n"
            "Some topics we can discuss:\n"
            "- Best train routes\n"
            "- Travel tips for train journeys\n"
            "- Railway station amenities and services\n\n"
            "Be creative and funny in just 2 lines.\n"
        )