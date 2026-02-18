import "./style.css";
import { parseHash } from "./router";
import { Layout } from "./pages/Layout";
import { HomePage } from "./pages/Home";
import { EnvironmentsPage } from "./pages/Environments";
import { EnvDocPage } from "./pages/EnvDoc";
import { ProfilePage } from "./pages/Profile";
import { PlayPage } from "./pages/Play";


const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("missing #app");

function render() {
  const r = parseHash();

  if (r.name === "home") {
    app.innerHTML = Layout("home", HomePage());
    return;
  }

  if (r.name === "environments") {
    app.innerHTML = Layout("environments", EnvironmentsPage(r.slug));
    return;
  }

  if (r.name === "doc") {
    app.innerHTML = Layout("environments", EnvDocPage(r.slug));
    return;
  }

  if (r.name === "play") {
    app.innerHTML = Layout("environments", PlayPage(r.slug));
    return;
  }


  if (r.name === "profile") {
    app.innerHTML = Layout("home", ProfilePage());
    return;
  }

  app.innerHTML = Layout("home", HomePage());
}

window.addEventListener("hashchange", render);
render();
