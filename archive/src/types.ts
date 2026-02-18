export type Difficulty = 0 | 1 | 2 | 3 | 4 | 5;

export type Environment = {
  slug: string;
  title: string;
  difficulty: Difficulty;
  description: string;
  docSections: { title: string; items: string[] }[];
  image?: {
    kind: "placeholder" | "url";
    value: string; // placeholder text or url
  };
};
