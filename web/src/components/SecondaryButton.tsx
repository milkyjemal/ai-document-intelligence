import * as React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement>;

export function SecondaryButton({ className, ...rest }: Props) {
  return (
    <button
      {...rest}
      className={`inline-flex items-center justify-center rounded-xl border border-zinc-200 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900 ${
        className ?? ""
      }`}
    />
  );
}
