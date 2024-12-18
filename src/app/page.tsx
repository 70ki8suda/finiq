import Link from 'next/link';
import { getCategories } from '@/lib/markdown';

export default function HomePage() {
  const categories = getCategories();

  return (
    <div>
      <h1>FINIQ</h1>
      <div>
        {categories.map((category) => (
          <Link
            key={category}
            href={`/${category}`}
            style={{
              display: 'block',
              padding: '1rem',
              margin: '0.5rem 0',
              border: '1px solid #eaeaea',
            }}
          >
            {category.toUpperCase()}
          </Link>
        ))}
      </div>
    </div>
  );
}
