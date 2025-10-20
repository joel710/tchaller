import re
import json
import sys

class SQLFixer:
    def __init__(self):
        # Regex pour trouver les chaînes de caractères qui ressemblent à des tableaux JSON
        # et qui contiennent des caractères Unicode ou des apostrophes non échappées.
        # Capture le contenu entre les crochets.
        self.json_array_pattern = re.compile(r"E?'\[(\"[^\"]*?\"(?:,\s*\"[^\"]*?\")*?)\]'", re.IGNORECASE)
        # Regex pour les caractères Unicode spécifiques qui posent problème
        self.unicode_pattern = re.compile(r'\\u00e9')
        # Regex pour les apostrophes non échappées dans les chaînes de caractères SQL
        # Cette regex est plus spécifique pour éviter de double-échapper les apostrophes déjà échappées
        self.unescaped_apostrophe_pattern = re.compile(r"(?<=[^\\])'")

    def fix_json_array_string(self, match):
        # Extrait le contenu du tableau JSON (ex: \"item1\", \"item2\")
        content = match.group(1)
        # Supprime les guillemets autour des éléments et les divise en une liste Python
        items = [item.strip('"') for item in content.split(', ')]
        # Échappe les apostrophes dans chaque élément et les entoure de guillemets doubles
        # pour le format de tableau PostgreSQL
        escaped_items = [f'"' + item.replace("'", "''") + f'"' for item in items]
        # Rejoint les éléments pour former le tableau PostgreSQL
        return f"ARRAY[{', '.join(escaped_items)}]"

    def fix_sql_file(self, input_filepath, output_filepath):
        print(f"Lecture du fichier: {input_filepath}")
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        print("Application des correctifs...")
        # 1. Remplacer les tableaux JSON-like par le format ARRAY de PostgreSQL
        content = self.json_array_pattern.sub(self.fix_json_array_string, content)
        
        # 2. Remplacer les séquences Unicode échappées par les caractères réels
        content = self.unicode_pattern.sub('é', content)

        # 3. Échapper les apostrophes non échappées (sauf celles déjà échappées)
        # Cette étape doit être faite après la conversion des tableaux pour éviter les interférences
        content = self.unescaped_apostrophe_pattern.sub("''", content)

        print(f"Écriture du fichier corrigé: {output_filepath}")
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Correction terminée.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_sql.py <input_file.sql> <output_file.sql>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    fixer = SQLFixer()
    fixer.fix_sql_file(input_file, output_file)