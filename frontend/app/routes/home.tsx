import type { Route } from "./+types/home";
import App from "../App"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Gemma 4 with weather tools" },
    { name: "description", content: "Welcome to the Gemma 4 with weather tools!" },
  ];
}

export default function Home() {
  return <App />;
}
