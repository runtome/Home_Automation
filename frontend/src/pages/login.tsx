import Head from "next/head";

import LoginForm from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <>
      <Head>
        <title>Sign in - Home Automation</title>
      </Head>
      <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4">
        <h1 className="mb-6 text-2xl font-semibold text-gray-900">Home Automation Platform</h1>
        <LoginForm />
      </main>
    </>
  );
}
