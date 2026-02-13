export type Route =
  | { name: "home" }
  | { name: "environments"; slug?: string }
  | { name: "doc"; slug: string }
  | { name: "play"; slug?: string }
  | { name: "profile" };

export function parseHash(): Route {
  const raw = (location.hash || "#/").replace(/^#/, "");
  const pathOnly = raw.split("?")[0] || "";
  const parts = pathOnly.split("/").filter(Boolean);

  // "#/" or "#"
  if (parts.length === 0) return { name: "home" };

  // "#/environments" or "#/environments/maze"
  if (parts[0] === "environments") {
    return { name: "environments", slug: parts[1] };
  }

  // "#/doc/maze"
  if (parts[0] === "doc" && parts[1]) return { name: "doc", slug: parts[1] };

  if (parts[0] === "play") return { name: "play", slug: parts[1] };


  if (parts[0] === "profile") return { name: "profile" };

  return { name: "home" };
}
