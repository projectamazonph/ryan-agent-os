import { redirect } from "next/navigation";
import { getToken } from "@/lib/api";

export default async function Home() {
  const token = await getToken();
  redirect(token ? "/dashboard" : "/login");
}
