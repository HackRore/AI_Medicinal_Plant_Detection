export default function AboutPage() {
    return (
        <div className="container mx-auto px-4 py-16">
            <div className="max-w-4xl mx-auto">
                <section className="text-center mb-16">
                    <h1 className="text-5xl font-bold text-primary-800 mb-6">About Us</h1>
                    <p className="text-xl text-gray-600 leading-relaxed">
                        Bridging the gap between traditional botanical knowledge and modern technology
                        to democratize access to herbal medicine.
                    </p>
                </section>

                <div className="grid md:grid-cols-2 gap-12 mb-20">
                    <div className="bg-white p-8 rounded-2xl shadow-lg border-t-4 border-primary-500">
                        <h2 className="text-2xl font-bold mb-4 text-gray-800">Our Mission</h2>
                        <p className="text-gray-600 leading-relaxed">
                            To create an accessible, accurate, and easy-to-use tool that helps people identify medicinal
                            plants in their surroundings. By combining deep learning with traditional Ayurvedic knowledge,
                            we aim to preserve and promote the use of natural remedies for common ailments.
                        </p>
                    </div>
                    <div className="bg-white p-8 rounded-2xl shadow-lg border-t-4 border-green-500">
                        <h2 className="text-2xl font-bold mb-4 text-gray-800">The Technology</h2>
                        <p className="text-gray-600 leading-relaxed">
                            We utilize a state-of-the-art ensemble of MobileNetV2 and Vision Transformers to ensure
                            high accuracy in leaf recognition. Our system is augmented by Google's Gemini Vision API
                            to provide human-like descriptions and multilingual support.
                        </p>
                    </div>
                </div>

                <section className="mb-20">
                    <h2 className="text-3xl font-bold text-center mb-12 text-primary-800">Meet the Team</h2>
                    <div className="grid md:grid-cols-2 gap-8">
                        {[
                            { name: "Madhura Wankhade", role: "Exam No: 24167" },
                            { name: "Ravindra Ahire", role: "Exam No: 24101" },
                            { name: "Samruddhi Gholap", role: "Exam No: 24116" },
                            { name: "Pranali Ghugarkar", role: "Exam No: 24117" }
                        ].map((member, idx) => (
                            <div key={idx} className="bg-white p-6 rounded-xl shadow-md flex items-center gap-4 hover:shadow-lg transition-shadow">
                                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold text-xl">
                                    {member.name.charAt(0)}
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg text-gray-800">{member.name}</h3>
                                    <p className="text-gray-500">{member.role}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="bg-gray-900 text-white p-12 rounded-3xl text-center">
                    <h2 className="text-3xl font-bold mb-6">Contact Us</h2>
                    <p className="text-lg opacity-80 mb-8">
                        Have questions, suggestions, or want to contribute? We'd love to hear from you.
                    </p>
                    <a
                        href="mailto:hackrore@gmail.com"
                        className="bg-white text-gray-900 px-8 py-3 rounded-full font-bold hover:bg-gray-100 transition-colors inline-block"
                    >
                        hackrore@gmail.com
                    </a>
                </section>
            </div>
        </div>
    )
}
