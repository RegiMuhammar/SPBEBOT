import { useEffect, useState } from "react";

type QueryState<T> = {
  data: T | null;
  error: string | null;
  loading: boolean;
};

export function useApiQuery<T>(loader: () => Promise<T>, deps: unknown[] = []) {
  const [state, setState] = useState<QueryState<T>>({
    data: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    let active = true;
    setState((current) => ({ ...current, loading: true, error: null }));

    loader()
      .then((data) => {
        if (!active) return;
        setState({ data, error: null, loading: false });
      })
      .catch((error: Error) => {
        if (!active) return;
        setState({ data: null, error: error.message, loading: false });
      });

    return () => {
      active = false;
    };
  }, deps);

  return state;
}
