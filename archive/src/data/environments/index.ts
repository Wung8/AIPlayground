import type { Environment } from "../../types";
import { slimeVolleyball } from "./slime-volleyball";
import { carRacing } from "./car-racing";
import { maze } from "./maze";

export const environments: Environment[] = [carRacing, maze, slimeVolleyball];

export function getEnv(slug: string): Environment | undefined {
  return environments.find((e) => e.slug === slug);
}
