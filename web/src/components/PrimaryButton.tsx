import * as React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
};

export function PrimaryButton({ loading, disabled, className, children, ...rest }: Props) {
  const isDisabled = Boolean(disabled || loading);

  return (
    <button
      {...rest}
      disabled={isDisabled}
      className={`inline-flex items-center justify-center rounded-xl bg-zinc-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-zinc-50 dark:text-zinc-950 dark:hover:bg-zinc-200 ${
        className ?? ""
      }`}
    >
      {loading ? "Processing…" : children}
    </button>
  );
}
