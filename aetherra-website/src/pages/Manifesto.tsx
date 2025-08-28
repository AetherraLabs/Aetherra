// ...existing code...

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Manifesto() {
    const [content, setContent] = useState('');

    useEffect(() => {
        fetch('/manifesto.md')
            .then((res) => res.text())
            .then(setContent);
    }, []);

    return (
        <div className="mx-auto max-w-4xl px-4 py-10 prose prose-invert prose-lg">
            <ReactMarkdown>{content}</ReactMarkdown>
        </div>
    );
}
